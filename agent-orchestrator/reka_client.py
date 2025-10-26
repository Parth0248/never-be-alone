"""Reka.ai API Client for multimodal context understanding.

Reka.ai provides advanced multimodal AI capabilities for:
- Enhanced text understanding
- Visual context interpretation (future: images from Snap Spectacles)
- Audio context analysis
- Structured output generation
"""
import httpx
import logging
import warnings
from typing import Dict, Any, Optional, List
from config import Config

# Suppress SSL warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class RekaClient:
    """Client for Reka.ai multimodal API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.REKA_API_KEY
        self.base_url = Config.REKA_BASE_URL
        self.model = Config.REKA_MODEL
        self.client = httpx.AsyncClient(timeout=30.0, verify=False)  # Disable SSL verification

    async def process_text(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Process text through Reka's multimodal model.

        Args:
            text: Input text to process
            context: Additional context (user_id, timestamp, etc.)
            system_prompt: Optional system prompt for structured output

        Returns:
            Dict containing:
                - enhanced_understanding: Reka's interpretation
                - entities: Extracted entities
                - intent_hints: Suggested intents
                - context_enrichment: Additional context
        """
        try:
            logger.info(f"🤖 [Reka] Processing text: {text[:100]}...")

            # Build user prompt with instructions
            user_prompt = f"""Analyze this user input and provide enhanced understanding.

User input: "{text}"

Provide your analysis in this JSON format:
{{
    "enhanced_understanding": "clear interpretation of what the user means",
    "entities": {{"entity_type": "value"}},
    "intent_hints": ["possible", "user", "intents"],
    "context_enrichment": "additional helpful context"
}}"""

            # Add context if provided
            if context:
                user_prompt += f"\n\nContext: User ID={context.get('uid')}, Timestamp={context.get('timestamp')}, Source={context.get('source')}"

            # Prepare request payload (single human message)
            payload = {
                "model_name": self.model,
                "conversation_history": [
                    {
                        "type": "human",
                        "text": user_prompt
                    }
                ],
                "temperature": 0.3,  # Lower for more structured output
                "max_tokens": 1000,
                "stream": stream  # Enable streaming if requested
            }

            logger.info(f"🌐 [Reka] Sending request to {self.base_url}/chat (stream={stream})")

            # Call Reka API
            if stream:
                # For streaming, we'll collect chunks
                return await self._process_stream(payload)
            else:
                # Regular request
                response = await self.client.post(
                    f"{self.base_url}/chat",
                    headers={
                        "X-Api-Key": self.api_key,
                        "Content-Type": "application/json"
                    },
                    json=payload
                )

            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ [Reka] Got response from Reka")

                # Reka returns format: {'type': 'model', 'text': '...', 'finish_reason': 'stop', 'metadata': {...}}
                response_text = data.get("text", "")

                # Try to parse as JSON
                import json
                try:
                    parsed_response = json.loads(response_text)
                    logger.info(f"✅ [Reka] Parsed structured response")
                except json.JSONDecodeError:
                    # If not JSON, create structured response from text
                    parsed_response = {
                        "enhanced_understanding": response_text,
                        "entities": {},
                        "intent_hints": ["general_query"],
                        "context_enrichment": ""
                    }
                    logger.info(f"ℹ️ [Reka] Response was plain text, using fallback structure")

                return {
                    "success": True,
                    "reka_response": parsed_response,
                    "raw_response": response_text,
                    "model": self.model,
                    "finish_reason": data.get("finish_reason", "unknown")
                }
            else:
                logger.error(f"❌ [Reka] API error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Reka API returned status {response.status_code}",
                    "status_code": response.status_code,
                    "response": response.text
                }

        except Exception as e:
            logger.error(f"❌ [Reka] Error processing text: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def process_multimodal(
        self,
        text: str,
        image_url: Optional[str] = None,
        audio_data: Optional[bytes] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process multimodal input (text + image/audio).

        Args:
            text: Text input
            image_url: URL to image (future: Snap Spectacles)
            audio_data: Audio bytes (future enhancement)
            context: Additional context

        Returns:
            Multimodal understanding from Reka
        """
        try:
            logger.info(f"🎥 [Reka] Processing multimodal input...")

            # Build multimodal payload
            media = []

            if image_url:
                media.append({
                    "type": "image_url",
                    "image_url": image_url
                })
                logger.info(f"📸 [Reka] Including image: {image_url}")

            if audio_data:
                # Future: Handle audio input
                logger.info(f"🎵 [Reka] Audio processing not yet implemented")

            payload = {
                "model_name": self.model,
                "conversation_history": [
                    {
                        "type": "human",
                        "text": f"Analyze this input:\n{text}",
                        "media_url": image_url if image_url else None
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 1500
            }

            # Call Reka API
            response = await self.client.post(
                f"{self.base_url}/chat",
                headers={
                    "X-Api-Key": self.api_key,
                    "Content-Type": "application/json"
                },
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                # Reka returns format: {'type': 'model', 'text': '...', 'finish_reason': 'stop', 'metadata': {...}}
                response_text = data.get("text", "")

                return {
                    "success": True,
                    "multimodal_understanding": response_text,
                    "media_analyzed": {
                        "image": image_url is not None,
                        "audio": audio_data is not None
                    },
                    "model": self.model
                }
            else:
                logger.error(f"❌ [Reka] Multimodal API error: {response.status_code}")
                return {
                    "success": False,
                    "error": f"Status {response.status_code}",
                    "response": response.text
                }

        except Exception as e:
            logger.error(f"❌ [Reka] Multimodal processing error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _process_stream(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process streaming response from Reka.

        Args:
            payload: Request payload with stream=True

        Returns:
            Aggregated response from stream
        """
        try:
            logger.info("🌊 [Reka] Starting stream processing...")

            full_response = ""
            reasoning_steps = []

            async with self.client.stream(
                "POST",
                f"{self.base_url}/chat",
                headers={
                    "X-Api-Key": self.api_key,
                    "Content-Type": "application/json"
                },
                json=payload
            ) as response:

                if response.status_code != 200:
                    error_text = await response.aread()
                    logger.error(f"❌ [Reka] Stream error: {response.status_code} - {error_text}")
                    return {
                        "success": False,
                        "error": f"Stream failed with status {response.status_code}"
                    }

                # Process SSE stream
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        chunk_data = line[6:]  # Remove "data: " prefix

                        if chunk_data == "[DONE]":
                            break

                        try:
                            import json
                            chunk = json.loads(chunk_data)

                            # Extract delta content
                            delta = chunk.get("choices", [{}])[0].get("delta", {})

                            # Collect reasoning steps
                            if delta.get("reasoning_steps"):
                                reasoning_steps.extend(delta["reasoning_steps"])
                                logger.info(f"💭 [Reka Stream] Reasoning: {delta['reasoning_steps'][-1].get('content', '')[:50]}...")

                            # Collect response content
                            if delta.get("content"):
                                full_response += delta["content"]
                                logger.info(f"📝 [Reka Stream] Content chunk: {delta['content'][:50]}...")

                        except json.JSONDecodeError:
                            continue

            logger.info(f"✅ [Reka] Stream complete - {len(full_response)} chars")

            # Try to parse final response as JSON
            import json
            try:
                parsed_response = json.loads(full_response)
            except:
                parsed_response = {
                    "enhanced_understanding": full_response,
                    "entities": {},
                    "intent_hints": ["general_query"],
                    "context_enrichment": ""
                }

            return {
                "success": True,
                "reka_response": parsed_response,
                "raw_response": full_response,
                "reasoning_steps": reasoning_steps,
                "model": self.model,
                "streamed": True
            }

        except Exception as e:
            logger.error(f"❌ [Reka] Stream processing error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def upload_video(self, video_data: bytes, video_name: str = "spectacles_feed.mp4") -> Optional[str]:
        """Upload video to Reka for processing.

        Args:
            video_data: Video file bytes
            video_name: Name of the video file

        Returns:
            Video ID for use in Q&A
        """
        try:
            logger.info(f"📹 [Reka] Uploading video: {video_name} ({len(video_data)} bytes)")

            # Upload video
            files = {"file": (video_name, video_data, "video/mp4")}

            response = await self.client.post(
                f"{self.base_url}/videos/upload",
                headers={"X-Api-Key": self.api_key},
                files=files
            )

            if response.status_code in [200, 201]:
                data = response.json()
                video_id = data.get("video_id")
                logger.info(f"✅ [Reka] Video uploaded - ID: {video_id}")
                return video_id
            else:
                logger.error(f"❌ [Reka] Video upload failed: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"❌ [Reka] Video upload error: {e}")
            return None

    async def video_qa(
        self,
        video_id: str,
        question: str,
        audio_transcript: Optional[str] = None,
        stream: bool = True
    ) -> Dict[str, Any]:
        """Ask questions about a video (with optional audio context).

        Args:
            video_id: Reka video ID from upload
            question: Question about the video
            audio_transcript: Optional Omi audio transcript for context
            stream: Enable streaming responses

        Returns:
            Answer from video Q&A
        """
        try:
            logger.info(f"🎥 [Reka Video Q&A] Question: {question}")

            # Build messages
            messages = []

            if audio_transcript:
                # Add audio context first
                messages.append({
                    "role": "user",
                    "content": f"Context from audio: {audio_transcript}"
                })
                logger.info(f"🎤 [Reka] Added audio context from Omi device")

            # Add the actual question
            messages.append({
                "role": "user",
                "content": question
            })

            payload = {
                "video_id": video_id,
                "messages": messages
            }

            if stream:
                logger.info("🌊 [Reka Video Q&A] Starting streaming response...")
                return await self._video_qa_stream(payload)
            else:
                # Non-streaming request
                response = await self.client.post(
                    f"{self.base_url}/qa",
                    headers={
                        "X-Api-Key": self.api_key,
                        "Content-Type": "application/json"
                    },
                    json=payload
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "answer": data.get("answer"),
                        "confidence": data.get("confidence"),
                        "video_id": video_id,
                        "question": question
                    }
                else:
                    logger.error(f"❌ [Reka Video Q&A] Failed: {response.status_code}")
                    return {
                        "success": False,
                        "error": f"Status {response.status_code}"
                    }

        except Exception as e:
            logger.error(f"❌ [Reka Video Q&A] Error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _video_qa_stream(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process streaming video Q&A response.

        Args:
            payload: Request payload with video_id and messages

        Returns:
            Aggregated streaming response
        """
        try:
            full_answer = ""

            async with self.client.stream(
                "POST",
                f"{self.base_url}/qa/stream",
                headers={
                    "X-Api-Key": self.api_key,
                    "Content-Type": "application/json"
                },
                json=payload
            ) as response:

                if response.status_code != 200:
                    error_text = await response.aread()
                    logger.error(f"❌ [Reka Video Stream] Error: {response.status_code} - {error_text}")
                    return {
                        "success": False,
                        "error": f"Stream failed: {response.status_code}"
                    }

                # Process SSE stream
                async for line in response.aiter_lines():
                    if not line:
                        continue

                    try:
                        import json
                        # Parse SSE event
                        event_data = json.loads(line)

                        if event_data.get("event") == "qa_stream":
                            data = event_data.get("data", {})
                            answer_chunk = data.get("answer", "")

                            if answer_chunk:
                                full_answer = answer_chunk  # Update with latest
                                logger.info(f"📝 [Reka Video Stream] {data.get('status')}: {answer_chunk[:50]}...")

                    except json.JSONDecodeError:
                        continue

            logger.info(f"✅ [Reka Video Q&A] Complete: {len(full_answer)} chars")

            return {
                "success": True,
                "answer": full_answer,
                "video_id": payload.get("video_id"),
                "question": payload.get("messages", [{}])[-1].get("content"),
                "streamed": True
            }

        except Exception as e:
            logger.error(f"❌ [Reka Video Stream] Error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global client instance
_reka_client: Optional[RekaClient] = None


def get_reka_client() -> RekaClient:
    """Get or create the global Reka client instance."""
    global _reka_client
    if _reka_client is None:
        _reka_client = RekaClient()
    return _reka_client
