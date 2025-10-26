"""
Webhook.site Data Fetcher
Polls webhook.site URLs to fetch Omi data and processes through our pipeline
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.reka_client import RekaClient
from src.omi_client import OmiClient

load_dotenv()

# Webhook.site URLs
AUDIO_WEBHOOK_URL = "https://webhook.site/token/7d8f3163-874e-4491-a29e-b0be42902456/requests"
IMAGE_WEBHOOK_URL = "https://webhook.site/token/4cbaf51e-538f-4bd9-9a0b-96da59c50a62/requests"

# Initialize clients
reka_client = RekaClient()
omi_client = OmiClient()

# Track processed requests
processed_audio_ids = set()
processed_image_ids = set()


def fetch_webhook_requests(webhook_url: str) -> List[Dict]:
    """
    Fetch requests from webhook.site

    Args:
        webhook_url: Webhook.site token URL

    Returns:
        List of request data
    """
    try:
        response = requests.get(webhook_url, timeout=10)
        response.raise_for_status()

        data = response.json()

        # webhook.site returns data structure with 'data' key containing requests
        if isinstance(data, dict) and 'data' in data:
            return data['data']
        elif isinstance(data, list):
            return data
        else:
            return []

    except Exception as e:
        print(f"Error fetching webhook data: {str(e)}")
        return []


def process_audio_request(request_data: Dict) -> Optional[Dict]:
    """
    Process audio transcript request from Omi pendant

    Args:
        request_data: Request data from webhook.site

    Returns:
        Processed transcript data
    """
    try:
        # Extract the content/payload
        content = request_data.get('content') or request_data.get('text_data')

        if not content:
            return None

        # Parse JSON if it's a string
        if isinstance(content, str):
            content = json.loads(content)

        # Extract transcript segments
        segments = content.get('segments', [])

        if not segments:
            return None

        # Combine all segments into full transcript
        transcript_parts = []
        for segment in segments:
            speaker = segment.get('speaker', 'Unknown')
            text = segment.get('text', '')
            transcript_parts.append(f"{speaker}: {text}")

        full_transcript = "\n".join(transcript_parts)

        return {
            "transcript": full_transcript,
            "segments": segments,
            "session_id": content.get('session_id'),
            "timestamp": request_data.get('created_at')
        }

    except Exception as e:
        print(f"Error processing audio request: {str(e)}")
        return None


def process_image_request(request_data: Dict) -> Optional[Dict]:
    """
    Process image/context request from Omi glasses

    Args:
        request_data: Request data from webhook.site

    Returns:
        Processed image/context data
    """
    try:
        # Extract the content/payload
        content = request_data.get('content') or request_data.get('text_data')

        if not content:
            return None

        # Parse JSON if it's a string
        if isinstance(content, str):
            content = json.loads(content)

        return {
            "images": content.get('photos', []),
            "context": content.get('structured', {}),
            "timestamp": request_data.get('created_at')
        }

    except Exception as e:
        print(f"Error processing image request: {str(e)}")
        return None


def process_combined_data(audio_data: Dict, image_data: Optional[Dict] = None):
    """
    Process combined audio and image data through our AI pipeline

    Args:
        audio_data: Audio transcript data
        image_data: Optional image/context data
    """
    try:
        print("\n" + "="*60)
        print("PROCESSING OMI DATA")
        print("="*60)
        print(f"Timestamp: {datetime.now().isoformat()}")

        # Extract transcript
        transcript = audio_data.get('transcript', '')
        print(f"\nTranscript length: {len(transcript)}")
        print(f"Preview: {transcript[:200]}...")

        # Extract images and context
        images_base64 = []
        context_overview = ""

        if image_data:
            images = image_data.get('images', [])
            for img in images:
                if 'base64' in img:
                    images_base64.append(img['base64'])

            context = image_data.get('context', {})
            title = context.get('title', '')
            overview = context.get('overview', '')
            context_overview = f"{title}\n\n{overview}"

            print(f"Images: {len(images_base64)}")
            print(f"Context length: {len(context_overview)}")

        # Process through Reka.AI
        print("\nProcessing through Reka.AI...")
        reka_result = reka_client.process_omi_data(
            images_base64=images_base64,
            audio_transcript=transcript,
            context_overview=context_overview,
            supermemory_context=""
        )

        if not reka_result['success']:
            print(f"Reka processing failed: {reka_result.get('error')}")
            return

        response_text = reka_result['response']
        print(f"\nReka response received ({len(response_text)} chars)")
        print(f"Response preview: {response_text[:200]}...")

        # Send to OMI app
        print("\nSending response to OMI app...")
        omi_result = omi_client.send_response(
            response_text=response_text,
            original_context=transcript[:500]
        )

        if omi_result['success']:
            print("Response sent to OMI app successfully!")
        else:
            print(f"Failed to send to OMI: {omi_result.get('error')}")

        # Store in Supermemory
        print("\nStoring in Supermemory...")
        # TODO: Add Supermemory storage via MCP

        print("\n" + "="*60)
        print("PROCESSING COMPLETE")
        print("="*60)

    except Exception as e:
        print(f"\nError in combined processing: {str(e)}")


def poll_webhooks(interval: int = 5):
    """
    Poll webhook.site URLs for new data

    Args:
        interval: Polling interval in seconds
    """
    print("="*60)
    print("WEBHOOK FETCHER STARTING")
    print("="*60)
    print(f"Audio webhook: {AUDIO_WEBHOOK_URL}")
    print(f"Image webhook: {IMAGE_WEBHOOK_URL}")
    print(f"Polling interval: {interval}s")
    print(f"Reka API: {'Configured' if reka_client.api_key else 'Not configured'}")
    print(f"OMI API: {'Configured' if omi_client.api_key else 'Not configured'}")
    print("="*60)
    print("\nWaiting for Omi data...\n")

    last_audio_data = None
    last_image_data = None

    try:
        while True:
            # Fetch audio requests
            audio_requests = fetch_webhook_requests(AUDIO_WEBHOOK_URL)

            for request in audio_requests:
                request_id = request.get('uuid') or request.get('id')

                if request_id and request_id not in processed_audio_ids:
                    audio_data = process_audio_request(request)

                    if audio_data:
                        processed_audio_ids.add(request_id)
                        last_audio_data = audio_data

                        print(f"\n[NEW AUDIO] Received at {audio_data['timestamp']}")
                        print(f"Session: {audio_data['session_id']}")
                        print(f"Segments: {len(audio_data['segments'])}")

                        # Process immediately if we have recent image data
                        if last_image_data:
                            process_combined_data(audio_data, last_image_data)
                        else:
                            print("Waiting for image data to combine...")

            # Fetch image requests
            image_requests = fetch_webhook_requests(IMAGE_WEBHOOK_URL)

            for request in image_requests:
                request_id = request.get('uuid') or request.get('id')

                if request_id and request_id not in processed_image_ids:
                    image_data = process_image_request(request)

                    if image_data:
                        processed_image_ids.add(request_id)
                        last_image_data = image_data

                        print(f"\n[NEW IMAGE] Received at {image_data['timestamp']}")
                        print(f"Images: {len(image_data['images'])}")

                        # Process immediately if we have recent audio data
                        if last_audio_data:
                            process_combined_data(last_audio_data, image_data)
                        else:
                            print("Waiting for audio data to combine...")

            # Sleep before next poll
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n\nStopping webhook fetcher...")
        print(f"Processed {len(processed_audio_ids)} audio requests")
        print(f"Processed {len(processed_image_ids)} image requests")


if __name__ == "__main__":
    # Start polling
    poll_webhooks(interval=5)
