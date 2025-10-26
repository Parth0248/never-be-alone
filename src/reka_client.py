"""
Reka.AI Client for Multimodal Processing
Handles images (base64), audio transcripts, and context from OMI devices
"""

import os
import requests
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class RekaClient:
    """Client for interacting with Reka.AI Chat API with multimodal support"""

    def __init__(self):
        self.api_key = os.getenv('REKA_API_KEY')
        self.model = os.getenv('REKA_MODEL', 'reka-flash')
        self.base_url = "https://api.reka.ai/v1"

        if not self.api_key:
            raise ValueError("REKA_API_KEY not found in environment variables")

    def process_omi_data(
        self,
        images_base64: List[str],
        audio_transcript: str,
        context_overview: str,
        supermemory_context: Optional[str] = None
    ) -> Dict:
        """
        Process OMI glasses data with multimodal analysis

        Args:
            images_base64: List of base64 encoded images from OMI glasses
            audio_transcript: Audio transcription from OMI device
            context_overview: Contextual summary from OMI app
            supermemory_context: Retrieved context from Supermemory (optional)

        Returns:
            Dict with Reka's analysis and response
        """
        # Build the multimodal message content
        content = []

        # Add images as data URLs
        for img_base64 in images_base64:
            content.append({
                "type": "image_url",
                "image_url": f"data:image/jpeg;base64,{img_base64}"
            })

        # Build the text prompt
        prompt_parts = []

        if context_overview:
            prompt_parts.append(f"**Scene Context from OMI Glasses:**\n{context_overview}")

        if audio_transcript:
            prompt_parts.append(f"\n**Audio Transcript:**\n{audio_transcript}")

        if supermemory_context:
            prompt_parts.append(f"\n**Relevant Memory Context:**\n{supermemory_context}")

        prompt_parts.append(
            "\n**Task:**\n"
            "Based on the images, audio transcript, and context provided, please:\n"
            "1. Analyze what the user is experiencing and doing\n"
            "2. Identify any questions, requests, or needs the user might have\n"
            "3. Provide helpful, actionable insights or responses\n"
            "4. If appropriate, suggest relevant actions or next steps\n\n"
            "Provide a clear, concise response that would be useful to the user."
        )

        # Add text content
        content.append({
            "type": "text",
            "text": "\n".join(prompt_parts)
        })

        # Call Reka API
        response = self._call_chat_api(content)

        return response

    def _call_chat_api(self, content: List[Dict]) -> Dict:
        """
        Call Reka Chat API with multimodal content

        Args:
            content: List of content items (images, text)

        Returns:
            Dict with API response
        """
        url = f"{self.base_url}/chat"

        headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "model": self.model,
            "stream": False
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            result = response.json()

            # Extract the response text
            if 'responses' in result and len(result['responses']) > 0:
                message_content = result['responses'][0].get('message', {}).get('content', '')

                return {
                    "success": True,
                    "response": message_content,
                    "model": self.model,
                    "raw_response": result
                }
            else:
                return {
                    "success": False,
                    "error": "No response content in API result",
                    "raw_response": result
                }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }

    def simple_query(self, text: str, images_base64: Optional[List[str]] = None) -> Dict:
        """
        Simple query with optional images

        Args:
            text: Text query
            images_base64: Optional list of base64 encoded images

        Returns:
            Dict with API response
        """
        content = []

        # Add images if provided
        if images_base64:
            for img_base64 in images_base64:
                content.append({
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{img_base64}"
                })

        # Add text
        content.append({
            "type": "text",
            "text": text
        })

        return self._call_chat_api(content)


# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("🤖 REKA CLIENT TEST")
    print("=" * 60)

    client = RekaClient()
    print(f"\n✅ Reka client initialized")
    print(f"   Model: {client.model}")
    print(f"   API Key: {client.api_key[:20]}...")

    # Test with simple text query
    print(f"\n🧪 Testing simple text query...")
    result = client.simple_query("What is the capital of France?")

    if result['success']:
        print(f"\n✅ Query successful!")
        print(f"\n📝 Response:\n{result['response']}")
    else:
        print(f"\n❌ Query failed: {result.get('error', 'Unknown error')}")

    print(f"\n" + "=" * 60)
