"""Supermemory API Client for real memory operations.

Uses Supermemory REST API endpoints:
- POST https://api.supermemory.ai/v3/documents (add memory)
- POST https://api.supermemory.ai/v4/search (search)
"""
import httpx
import logging
from typing import Dict, Any, Optional
from config import Config

logger = logging.getLogger(__name__)


class SupermemoryMCPClient:
    """Client for Supermemory API operations."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or Config.SUPERMEMORY_API_KEY
        self.base_url = "https://api.supermemory.ai"
        self.client = httpx.AsyncClient(timeout=10.0)

    async def call_tool(self, function_name: str, **kwargs) -> Dict[str, Any]:
        """Call a Supermemory function.

        Args:
            function_name: Name of the function (search, addMemory, whoAmI)
            **kwargs: Function arguments

        Returns:
            Result from Supermemory
        """
        if function_name == "search":
            return await self.search(**kwargs)
        elif function_name == "addMemory":
            return await self.add_memory(**kwargs)
        elif function_name == "whoAmI":
            return await self.who_am_i()
        else:
            return {
                "success": False,
                "error": f"Unknown function: {function_name}"
            }

    async def search(self, informationToGet: str) -> Dict[str, Any]:
        """Search Supermemory.

        Args:
            informationToGet: Query string

        Returns:
            Search results
        """
        try:
            logger.info(f"[Supermemory API] 🔍 Searching for: {informationToGet}")

            response = await self.client.post(
                f"{self.base_url}/v4/search",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "q": informationToGet,
                    "limit": 10
                }
            )

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                logger.info(f"[Supermemory API] ✅ Found {len(results)} results")

                return {
                    "success": True,
                    "query": informationToGet,
                    "results": results,
                    "count": len(results)
                }
            else:
                logger.error(f"[Supermemory API] ❌ Search failed: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API returned status {response.status_code}",
                    "status_code": response.status_code,
                    "response": response.text
                }

        except Exception as e:
            logger.error(f"[Supermemory API] ❌ Search error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def add_memory(self, thingToRemember: str, containerTag: str = "omi_transcription") -> Dict[str, Any]:
        """Add a memory to Supermemory.

        Args:
            thingToRemember: Content to store
            containerTag: Tag to organize memories (default: omi_transcription)

        Returns:
            Storage result
        """
        try:
            logger.info(f"[Supermemory API] 💾 Storing memory: {thingToRemember[:100]}...")

            response = await self.client.post(
                f"{self.base_url}/v3/documents",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "content": thingToRemember,
                    "containerTag": containerTag,
                    "metadata": {}
                }
            )

            if response.status_code in [200, 201]:
                data = response.json()
                logger.info(f"[Supermemory API] ✅ Memory stored successfully - ID: {data.get('id', 'N/A')}")

                return {
                    "success": True,
                    "content": thingToRemember,
                    "result": data
                }
            else:
                logger.error(f"[Supermemory API] ❌ Add memory failed: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API returned status {response.status_code}",
                    "status_code": response.status_code,
                    "response": response.text
                }

        except Exception as e:
            logger.error(f"[Supermemory API] ❌ Add memory error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def who_am_i(self) -> Dict[str, Any]:
        """Get current user information.

        Returns:
            User information
        """
        try:
            logger.info("[Supermemory API] Getting user information")

            # Supermemory doesn't have a dedicated whoami endpoint
            # Return basic info based on API key
            return {
                "success": True,
                "user": "authenticated",
                "api_key_prefix": self.api_key[:15] + "..." if self.api_key else "none"
            }

        except Exception as e:
            logger.error(f"[Supermemory API] WhoAmI error: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Global client instance
_mcp_client: Optional[SupermemoryMCPClient] = None


def get_mcp_client() -> SupermemoryMCPClient:
    """Get or create the global client instance."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = SupermemoryMCPClient()
    return _mcp_client
