"""Context Retrieval Agent - Searches and retrieves information from Supermemory."""
from typing import Dict, Any, List
import requests
from .base_agent import BaseAgent
from config import Config


class ContextRetrievalAgent(BaseAgent):
    """Agent that retrieves context from Supermemory."""

    def __init__(self):
        super().__init__(
            name="context_retrieval_agent",
            description="Searches Supermemory for relevant context and answers questions based on stored memories"
        )
        self.supermemory_api_key = Config.SUPERMEMORY_API_KEY
        self.supermemory_base_url = Config.SUPERMEMORY_BASE_URL

    async def handle_task(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle context retrieval tasks.

        Args:
            action: Action to perform (search, get_context, answer_question)
            params: Parameters for the action

        Returns:
            Task result
        """
        if action == "search":
            return await self._search(params)
        elif action == "get_context":
            return await self._get_context(params)
        elif action == "answer_question":
            return await self._answer_question(params)
        elif action == "store_memory":
            return await self._store_memory(params)
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}",
                "message": "Action not supported"
            }

    async def _search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search Supermemory for relevant memories.

        Args:
            params: Dict containing:
                - query: Search query
                - limit: Optional limit on results (default: 5)
                - user_id: Optional user ID filter

        Returns:
            Search results
        """
        query = params.get("query", "")
        limit = params.get("limit", 5)

        if not query:
            return {
                "success": False,
                "error": "No query provided",
                "message": "Query is required for search"
            }

        try:
            # Call Supermemory API - using the correct endpoint
            response = requests.post(
                f"{self.supermemory_base_url}/api/search",
                headers={
                    "Authorization": f"Bearer {self.supermemory_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "query": query,
                    "limit": limit
                },
                timeout=10
            )

            if response.status_code == 200:
                results = response.json()

                return {
                    "success": True,
                    "result": {
                        "query": query,
                        "results": results.get("memories", []),
                        "count": len(results.get("memories", []))
                    },
                    "message": f"Found {len(results.get('memories', []))} results"
                }
            else:
                return {
                    "success": False,
                    "error": f"API returned status {response.status_code}",
                    "message": "Search failed"
                }

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Supermemory API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to connect to Supermemory"
            }

    async def _get_context(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get context for a specific topic or time period.

        Args:
            params: Dict containing:
                - topic: Topic to get context for
                - time_range: Optional time range filter
                - user_id: Optional user ID

        Returns:
            Context results
        """
        topic = params.get("topic", "")

        # Search for relevant memories
        search_result = await self._search({
            "query": topic,
            "limit": 10
        })

        if not search_result.get("success"):
            return search_result

        # Organize results by relevance
        memories = search_result["result"]["results"]

        return {
            "success": True,
            "result": {
                "topic": topic,
                "context": self._format_context(memories),
                "memories": memories,
                "count": len(memories)
            },
            "message": f"Retrieved context for '{topic}'"
        }

    async def _answer_question(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Answer a question using stored context.

        Args:
            params: Dict containing:
                - question: Question to answer
                - user_id: Optional user ID

        Returns:
            Answer based on context
        """
        question = params.get("question", "")

        if not question:
            return {
                "success": False,
                "error": "No question provided",
                "message": "Question is required"
            }

        # Search for relevant memories
        search_result = await self._search({
            "query": question,
            "limit": 5
        })

        if not search_result.get("success"):
            return {
                "success": False,
                "error": "Could not find relevant information",
                "message": "No context found to answer the question"
            }

        memories = search_result["result"]["results"]

        if not memories:
            return {
                "success": True,
                "result": {
                    "question": question,
                    "answer": "I don't have any stored information to answer that question.",
                    "confidence": 0.0
                },
                "message": "No relevant memories found"
            }

        # Format answer from memories
        # In production, would use LLM to generate natural language answer
        answer = self._generate_answer(question, memories)

        return {
            "success": True,
            "result": {
                "question": question,
                "answer": answer,
                "sources": memories,
                "confidence": 0.8
            },
            "message": "Question answered using stored context"
        }

    async def _store_memory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Store new memory in Supermemory.

        Args:
            params: Dict containing:
                - content: Memory content
                - metadata: Optional metadata

        Returns:
            Storage result
        """
        content = params.get("content", "")

        if not content:
            return {
                "success": False,
                "error": "No content provided",
                "message": "Content is required to store memory"
            }

        try:
            response = requests.post(
                f"{self.supermemory_base_url}/api/add",
                headers={
                    "Authorization": f"Bearer {self.supermemory_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "content": content,
                    "metadata": params.get("metadata", {})
                },
                timeout=10
            )

            if response.status_code in [200, 201]:
                result = response.json()

                return {
                    "success": True,
                    "result": {
                        "memory_id": result.get("id"),
                        "content": content
                    },
                    "message": "Memory stored successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"API returned status {response.status_code}",
                    "message": "Failed to store memory"
                }

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Supermemory API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to connect to Supermemory"
            }

    def _format_context(self, memories: List[Dict[str, Any]]) -> str:
        """Format memories into readable context.

        Args:
            memories: List of memory objects

        Returns:
            Formatted context string
        """
        if not memories:
            return "No context available."

        context_parts = []

        for i, memory in enumerate(memories, 1):
            content = memory.get("content", "")
            timestamp = memory.get("timestamp", "")

            if timestamp:
                context_parts.append(f"{i}. [{timestamp}] {content}")
            else:
                context_parts.append(f"{i}. {content}")

        return "\n".join(context_parts)

    def _generate_answer(self, question: str, memories: List[Dict[str, Any]]) -> str:
        """Generate an answer to a question based on memories.

        Args:
            question: Question asked
            memories: Relevant memories

        Returns:
            Answer string
        """
        # Simple answer generation - in production, use LLM
        if not memories:
            return "I don't have any information about that."

        # Extract most relevant memory
        most_relevant = memories[0]
        content = most_relevant.get("content", "")

        # Check if question asks for specific information
        question_lower = question.lower()

        if "when" in question_lower:
            timestamp = most_relevant.get("timestamp", "")
            if timestamp:
                return f"Based on my memory: {content} (from {timestamp})"

        if "what" in question_lower or "who" in question_lower or "where" in question_lower:
            return f"Based on what I remember: {content}"

        # Default: return most relevant memory
        if len(memories) == 1:
            return f"I found this: {content}"
        else:
            formatted_context = self._format_context(memories[:3])
            return f"I found several relevant memories:\n{formatted_context}"

    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities."""
        return {
            "name": self.name,
            "description": self.description,
            "actions": [
                {
                    "name": "search",
                    "description": "Search Supermemory for relevant information",
                    "params": ["query", "limit", "user_id"]
                },
                {
                    "name": "get_context",
                    "description": "Get context for a specific topic",
                    "params": ["topic", "time_range", "user_id"]
                },
                {
                    "name": "answer_question",
                    "description": "Answer questions using stored context",
                    "params": ["question", "user_id"]
                },
                {
                    "name": "store_memory",
                    "description": "Store new memory in Supermemory",
                    "params": ["content", "metadata"]
                }
            ],
            "integrations": ["Supermemory API"]
        }
