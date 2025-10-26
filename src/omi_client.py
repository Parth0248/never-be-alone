"""
OMI App API Client
Sends responses and creates memories/conversations in the OMI app
"""

import os
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class OmiClient:
    """Client for interacting with OMI App API"""

    def __init__(self):
        self.api_key = os.getenv('OMI_API_KEY')
        self.app_id = os.getenv('OMI_APP_ID')
        self.user_id = os.getenv('OMI_USER_ID')
        self.base_url = "https://api.omi.me/v2"

        if not self.api_key:
            raise ValueError("OMI_API_KEY not found in environment variables")
        if not self.app_id:
            raise ValueError("OMI_APP_ID not found in environment variables")

    def create_conversation(
        self,
        text: str,
        text_source: str = "other_text",
        text_source_spec: str = "ai_assistant",
        language: str = "en",
        started_at: Optional[str] = None,
        finished_at: Optional[str] = None
    ) -> Dict:
        """
        Create a conversation in the user's OMI account

        Args:
            text: The conversation text content
            text_source: Source type (audio_transcript, message, other_text)
            text_source_spec: Additional specification about the source
            language: Language code (default: "en")
            started_at: ISO 8601 timestamp (optional, defaults to now)
            finished_at: ISO 8601 timestamp (optional, defaults to started_at)

        Returns:
            Dict with API response
        """
        if not self.user_id or self.user_id == "your_omi_user_id_here":
            return {
                "success": False,
                "error": "OMI_USER_ID not configured. Please set it in .env file"
            }

        url = f"{self.base_url}/integrations/{self.app_id}/user/conversations"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Use current time if not provided
        if not started_at:
            started_at = datetime.now().isoformat() + "Z"
        if not finished_at:
            finished_at = started_at

        payload = {
            "started_at": started_at,
            "finished_at": finished_at,
            "language": language,
            "text": text,
            "text_source": text_source,
            "text_source_spec": text_source_spec
        }

        params = {"uid": self.user_id}

        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                params=params,
                timeout=30
            )
            response.raise_for_status()

            return {
                "success": True,
                "message": "Conversation created successfully",
                "status_code": response.status_code
            }

        except requests.exceptions.RequestException as e:
            error_detail = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                except:
                    error_detail = e.response.text

            return {
                "success": False,
                "error": f"Failed to create conversation: {error_detail}",
                "status_code": e.response.status_code if hasattr(e, 'response') else None
            }

    def create_memories(
        self,
        text: Optional[str] = None,
        memories: Optional[List[Dict]] = None,
        text_source: str = "other",
        text_source_spec: str = "ai_assistant"
    ) -> Dict:
        """
        Create memories in the user's OMI account

        Args:
            text: Text to extract memories from (optional if memories provided)
            memories: List of explicit memory objects with 'content' and 'tags' (optional)
            text_source: Source type (email, social_post, other)
            text_source_spec: Additional specification about the source

        Returns:
            Dict with API response
        """
        if not self.user_id or self.user_id == "your_omi_user_id_here":
            return {
                "success": False,
                "error": "OMI_USER_ID not configured. Please set it in .env file"
            }

        if not text and not memories:
            return {
                "success": False,
                "error": "Either text or memories must be provided"
            }

        url = f"{self.base_url}/integrations/{self.app_id}/user/memories"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "text_source": text_source,
            "text_source_spec": text_source_spec
        }

        if text:
            payload["text"] = text
        if memories:
            payload["memories"] = memories

        params = {"uid": self.user_id}

        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                params=params,
                timeout=30
            )
            response.raise_for_status()

            return {
                "success": True,
                "message": "Memories created successfully",
                "status_code": response.status_code
            }

        except requests.exceptions.RequestException as e:
            error_detail = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                except:
                    error_detail = e.response.text

            return {
                "success": False,
                "error": f"Failed to create memories: {error_detail}",
                "status_code": e.response.status_code if hasattr(e, 'response') else None
            }

    def send_notification(self, text: str) -> Dict:
        """
        Send a text notification to the user

        Args:
            text: Notification text

        Returns:
            Dict with API response

        Note: This creates a conversation which acts as a notification in the OMI app
        """
        return self.create_conversation(
            text=text,
            text_source="message",
            text_source_spec="ai_notification"
        )

    def send_response(self, response_text: str, original_context: Optional[str] = None) -> Dict:
        """
        Send an AI assistant response to the user

        Args:
            response_text: The response text from the AI
            original_context: Optional context about what prompted this response

        Returns:
            Dict with API response
        """
        if original_context:
            full_text = f"AI Assistant Response:\n\n{response_text}\n\n---\nContext: {original_context}"
        else:
            full_text = f"AI Assistant Response:\n\n{response_text}"

        return self.create_conversation(
            text=full_text,
            text_source="other_text",
            text_source_spec="ai_assistant_response"
        )

    def read_conversations(
        self,
        limit: int = 10,
        offset: int = 0,
        include_discarded: bool = False
    ) -> Dict:
        """
        Read conversations from the user's OMI account

        Args:
            limit: Maximum number of conversations to return (default: 10, max: 1000)
            offset: Number of conversations to skip (for pagination)
            include_discarded: Whether to include discarded conversations

        Returns:
            Dict with conversations list or error
        """
        if not self.user_id or self.user_id == "your_omi_user_id_here":
            return {
                "success": False,
                "error": "OMI_USER_ID not configured. Please set it in .env file"
            }

        url = f"{self.base_url}/integrations/{self.app_id}/conversations"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        params = {
            "uid": self.user_id,
            "limit": min(limit, 1000),  # Cap at 1000
            "offset": offset,
            "include_discarded": include_discarded
        }

        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            return {
                "success": True,
                "conversations": data.get("conversations", []),
                "count": len(data.get("conversations", [])),
                "status_code": response.status_code
            }

        except requests.exceptions.RequestException as e:
            error_detail = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                except:
                    error_detail = e.response.text

            return {
                "success": False,
                "error": f"Failed to read conversations: {error_detail}",
                "status_code": e.response.status_code if hasattr(e, 'response') else None
            }

    def read_memories(
        self,
        limit: int = 10,
        offset: int = 0
    ) -> Dict:
        """
        Read memories from the user's OMI account

        Args:
            limit: Maximum number of memories to return (default: 10, max: 1000)
            offset: Number of memories to skip (for pagination)

        Returns:
            Dict with memories list or error
        """
        if not self.user_id or self.user_id == "your_omi_user_id_here":
            return {
                "success": False,
                "error": "OMI_USER_ID not configured. Please set it in .env file"
            }

        url = f"{self.base_url}/integrations/{self.app_id}/memories"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        params = {
            "uid": self.user_id,
            "limit": min(limit, 1000),  # Cap at 1000
            "offset": offset
        }

        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            return {
                "success": True,
                "memories": data.get("memories", []),
                "count": len(data.get("memories", [])),
                "status_code": response.status_code
            }

        except requests.exceptions.RequestException as e:
            error_detail = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                except:
                    error_detail = e.response.text

            return {
                "success": False,
                "error": f"Failed to read memories: {error_detail}",
                "status_code": e.response.status_code if hasattr(e, 'response') else None
            }


# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("📱 OMI CLIENT TEST")
    print("=" * 60)

    client = OmiClient()
    print(f"\n✅ OMI client initialized")
    print(f"   App ID: {client.app_id}")
    print(f"   User ID: {client.user_id}")
    print(f"   API Key: {client.api_key[:20]}...")

    # Test sending a notification
    print(f"\n🧪 Testing notification...")

    if client.user_id and client.user_id != "your_omi_user_id_here":
        result = client.send_notification(
            "This is a test notification from your AI assistant!"
        )

        if result['success']:
            print(f"\n✅ Notification sent successfully!")
            print(f"   Status: {result.get('message')}")
        else:
            print(f"\n❌ Notification failed: {result.get('error')}")
    else:
        print(f"\n⚠️  Cannot test: OMI_USER_ID not configured in .env file")
        print(f"   Please set your OMI user ID to test the API")

    print(f"\n" + "=" * 60)
