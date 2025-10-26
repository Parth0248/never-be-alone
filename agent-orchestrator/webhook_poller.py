"""Webhook.site Poller - Fetches Omi transcriptions from webhook.site and processes them."""
import requests
import logging
import time
import asyncio
import sys
from datetime import datetime
from typing import Dict, Any, List, Set
from orchestrator import get_orchestrator

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Webhook.site configuration
WEBHOOK_SITE_TOKEN = "8d1347f7-8dfd-4d6f-803d-bd08f9a571c9"
WEBHOOK_SITE_API = f"https://webhook.site/token/{WEBHOOK_SITE_TOKEN}/requests"

# Polling configuration
POLL_INTERVAL_SECONDS = 5  # Poll every 5 seconds
MAX_REQUESTS_PER_POLL = 50  # Fetch up to 50 requests at a time


class WebhookSitePoller:
    """Polls webhook.site for new Omi transcriptions and processes them."""

    def __init__(self):
        self.orchestrator = get_orchestrator()
        self.processed_request_ids: Set[str] = set()
        self.last_poll_time = None

    def fetch_webhook_requests(self) -> List[Dict[str, Any]]:
        """Fetch recent requests from webhook.site.

        Returns:
            List of webhook requests
        """
        try:
            logger.info(f"📡 [WEBHOOK GET] Fetching requests from webhook.site...")
            print(f"\n{'='*80}")
            print(f"🌐 GET REQUEST: {WEBHOOK_SITE_API}")
            print(f"{'='*80}")

            response = requests.get(
                WEBHOOK_SITE_API,
                params={
                    "sorting": "newest",
                    "per_page": MAX_REQUESTS_PER_POLL
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                requests_data = data.get("data", [])
                logger.info(f"✅ [WEBHOOK GET] Fetched {len(requests_data)} requests from webhook.site")
                print(f"✅ Fetched {len(requests_data)} webhook requests")
                print(f"{'='*80}\n")
                return requests_data
            else:
                logger.error(f"❌ [WEBHOOK GET] Failed to fetch from webhook.site: {response.status_code}")
                print(f"❌ Failed with status: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"❌ [WEBHOOK GET] Error fetching from webhook.site: {e}")
            print(f"❌ Error: {e}")
            return []

    def parse_omi_transcription(self, webhook_request: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Omi transcription from webhook request.

        Args:
            webhook_request: Webhook.site request data

        Returns:
            Parsed transcription data or None if not valid
        """
        try:
            # Extract request body
            content = webhook_request.get("content", "")
            request_id = webhook_request.get("uuid", "unknown")

            print(f"\n📦 [PARSING] Request ID: {request_id}")
            print(f"   Raw content length: {len(content)} chars")

            # Try to parse as JSON
            import json
            try:
                body = json.loads(content)
                print(f"   ✅ Parsed as JSON")
            except:
                # If not JSON, treat as plain text
                body = {"text": content}
                print(f"   ⚠️  Not JSON, treating as plain text")

            # Extract transcription text
            transcription_text = ""

            # Handle Omi segment format
            if "segments" in body:
                segments = body.get("segments", [])
                transcription_text = " ".join([seg.get("text", "") for seg in segments if seg.get("text")])
                print(f"   📝 Found {len(segments)} segments")

            # Handle simple format
            elif "transcription" in body:
                transcription_text = body.get("transcription", "")
                print(f"   📝 Found 'transcription' field")

            # Handle text field directly
            elif "text" in body:
                transcription_text = body.get("text", "")
                print(f"   📝 Found 'text' field")

            if not transcription_text:
                print(f"   ❌ No transcription text found, skipping")
                return None

            print(f"   ✅ TRANSCRIPTION: \"{transcription_text[:100]}{'...' if len(transcription_text) > 100 else ''}\"")

            # Build context
            # Prioritize Omi device timestamp if available, otherwise use webhook.site timestamp
            current_time = datetime.now().isoformat()

            # Check if Omi sent timestamps (for future compatibility)
            omi_timestamp = body.get("created_at") or body.get("finished_at") or body.get("started_at")

            # Use Omi timestamp if available, otherwise webhook.site timestamp, finally current time
            timestamp = omi_timestamp or webhook_request.get("created_at") or current_time

            context = {
                "uid": body.get("uid") or body.get("user_id") or body.get("session_id", "unknown"),
                "timestamp": timestamp,
                "source": "omi_device_via_webhook_site",
                "session_id": body.get("session_id"),
                "webhook_request_id": webhook_request.get("uuid"),
                "ip_address": webhook_request.get("ip"),
                "user_agent": webhook_request.get("user_agent"),
                "processed_at": current_time
            }

            print(f"   👤 User ID: {context['uid']}")
            print(f"   ⏰ Timestamp: {context['timestamp']}")
            print(f"   🕐 Processed at: {current_time}")

            return {
                "transcription": transcription_text,
                "context": context,
                "raw_body": body
            }

        except Exception as e:
            logger.error(f"❌ Error parsing transcription: {e}")
            print(f"   ❌ Error: {e}")
            return None

    async def process_transcription(self, transcription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process transcription through orchestrator.

        Args:
            transcription_data: Parsed transcription data

        Returns:
            Processing result
        """
        try:
            transcription = transcription_data["transcription"]
            context = transcription_data["context"]

            print(f"\n{'='*80}")
            print(f"🎯 [ORCHESTRATOR] Processing transcription...")
            print(f"   Text: \"{transcription[:100]}{'...' if len(transcription) > 100 else ''}\"")
            print(f"{'='*80}")

            logger.info(f"🎯 [ORCHESTRATOR] Processing transcription: {transcription[:100]}...")

            result = await self.orchestrator.process_transcription(transcription, context)

            print(f"\n✅ [ORCHESTRATOR] Processed successfully!")
            print(f"   Intent: {result.get('intent')}")
            print(f"   Actions: {result.get('actions_taken')}")
            print(f"{'='*80}\n")

            logger.info(f"✅ [ORCHESTRATOR] Processed: {result.get('intent')} - {result.get('actions_taken')}")

            return result

        except Exception as e:
            logger.error(f"❌ [ORCHESTRATOR] Error processing transcription: {e}")
            print(f"❌ [ORCHESTRATOR] Error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def poll_and_process(self):
        """Poll webhook.site and process new transcriptions."""
        logger.info("Starting webhook.site poller...")

        while True:
            try:
                # Fetch requests from webhook.site
                webhook_requests = self.fetch_webhook_requests()

                if webhook_requests:
                    # Process new requests (ones we haven't seen before)
                    new_requests = [
                        req for req in webhook_requests
                        if req.get("uuid") not in self.processed_request_ids
                    ]

                    if new_requests:
                        print(f"\n🆕 Found {len(new_requests)} NEW requests to process")
                        logger.info(f"🆕 Found {len(new_requests)} new requests to process")
                    else:
                        print(f"⏸️  No new requests (already processed {len(self.processed_request_ids)} requests)")

                    for webhook_request in new_requests:
                        request_id = webhook_request.get("uuid")

                        print(f"\n{'─'*80}")
                        print(f"🔄 Processing request {request_id}")

                        # Parse transcription
                        transcription_data = self.parse_omi_transcription(webhook_request)

                        if transcription_data:
                            # Process through orchestrator
                            result = await self.process_transcription(transcription_data)

                            # Mark as processed
                            self.processed_request_ids.add(request_id)

                            print(f"✅ Successfully processed request {request_id}")
                            print(f"{'─'*80}\n")
                            logger.info(f"✅ Successfully processed request {request_id}")
                        else:
                            # Not a valid Omi transcription, skip it
                            self.processed_request_ids.add(request_id)
                            print(f"⏭️  Skipped request {request_id} (not a valid transcription)")
                            print(f"{'─'*80}\n")
                            logger.debug(f"⏭️  Skipped request {request_id} (not a valid transcription)")

                self.last_poll_time = datetime.now()

                # Wait before next poll
                await asyncio.sleep(POLL_INTERVAL_SECONDS)

            except KeyboardInterrupt:
                logger.info("Poller stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                await asyncio.sleep(POLL_INTERVAL_SECONDS)


async def main():
    """Main entry point."""
    logger.info("=" * 80)
    logger.info("Webhook.site Poller Starting")
    logger.info("=" * 80)
    logger.info(f"Webhook.site URL: https://webhook.site/{WEBHOOK_SITE_TOKEN}")
    logger.info(f"Poll interval: {POLL_INTERVAL_SECONDS} seconds")
    logger.info("=" * 80)
    logger.info("")
    logger.info("Waiting for Omi transcriptions from webhook.site...")
    logger.info("")

    poller = WebhookSitePoller()
    await poller.poll_and_process()


if __name__ == "__main__":
    asyncio.run(main())
