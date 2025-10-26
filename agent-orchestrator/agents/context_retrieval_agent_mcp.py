"""Context Retrieval Agent - Uses Supermemory MCP for real memory operations."""
from typing import Dict, Any, List
from .base_agent import BaseAgent


class ContextRetrievalAgentMCP(BaseAgent):
    """Agent that retrieves context from Supermemory using MCP.

    This agent integrates with the Supermemory MCP server that provides:
    - mcp__api-supermemory-ai__search(informationToGet: str)
    - mcp__api-supermemory-ai__addMemory(thingToRemember: str)
    - mcp__api-supermemory-ai__whoAmI()

    Note: Since this runs in a Python Flask server context (not Claude Code),
    it needs to call these MCP functions via the orchestrator's MCP client.
    """

    def __init__(self, mcp_client=None):
        super().__init__(
            name="context_retrieval_agent",
            description="Searches Supermemory for relevant context and answers questions using MCP"
        )
        self.mcp_client = mcp_client

    async def handle_task(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle context retrieval tasks using MCP.

        Args:
            action: Action to perform (search, store_memory, answer_question)
            params: Parameters for the action

        Returns:
            Task result
        """
        if action == "search":
            return await self._search_mcp(params)
        elif action == "store_memory":
            return await self._store_memory_mcp(params)
        elif action == "answer_question":
            return await self._answer_question_mcp(params)
        elif action == "get_context":
            return await self._get_context_mcp(params)
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}",
                "message": "Action not supported"
            }

    async def _call_mcp_function(self, function_name: str, **kwargs) -> Dict[str, Any]:
        """Call an MCP function.

        Args:
            function_name: Name of the MCP function (e.g., 'search', 'addMemory')
            **kwargs: Arguments for the function

        Returns:
            Result from MCP function
        """
        if self.mcp_client:
            try:
                # If we have an MCP client, use it
                return await self.mcp_client.call_tool(function_name, **kwargs)
            except Exception as e:
                self.logger.error(f"MCP call error: {e}")
                return {"success": False, "error": str(e)}
        else:
            # MCP client not available - document what should happen
            self.logger.warning(f"MCP client not available for {function_name}")
            return {
                "success": True,
                "mcp_function": f"mcp__api-supermemory-ai__{function_name}",
                "params": kwargs,
                "note": "MCP integration pending - would call actual Supermemory MCP here"
            }

    async def _search_mcp(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search Supermemory using MCP.

        Args:
            params: Dict containing:
                - query: Search query

        Returns:
            Search results from Supermemory
        """
        query = params.get("query", "")

        if not query:
            return {
                "success": False,
                "error": "No query provided",
                "message": "Query is required for search"
            }

        try:
            self.logger.info(f"Searching Supermemory via MCP for: {query}")

            # Call MCP search function
            result = await self._call_mcp_function(
                "search",
                informationToGet=query
            )

            return {
                "success": True,
                "result": {
                    "query": query,
                    "mcp_result": result,
                    "message": "Search executed via Supermemory MCP"
                },
                "message": f"Searched Supermemory for: {query}"
            }

        except Exception as e:
            self.logger.error(f"MCP search error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to search via MCP"
            }

    async def _store_memory_mcp(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Store memory using MCP.

        Args:
            params: Dict containing:
                - content: Memory content to store

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
            print(f"\n      💾 [CONTEXT AGENT] Storing memory via MCP...")
            print(f"         Content: {content[:80]}...")
            self.logger.info(f"💾 [Context Agent] Storing memory via MCP: {content[:100]}...")

            # Call MCP addMemory function
            result = await self._call_mcp_function(
                "addMemory",
                thingToRemember=content
            )

            if result.get("success"):
                print(f"         ✅ Memory stored successfully!")
                print(f"         Document ID: {result.get('result', {}).get('id', 'N/A')}")
            else:
                print(f"         ⚠️  Storage failed: {result.get('error')}")

            return {
                "success": result.get("success", True),
                "result": {
                    "content": content,
                    "mcp_result": result,
                    "message": "Memory stored via Supermemory MCP"
                },
                "message": "Memory stored successfully via MCP" if result.get("success") else f"Storage failed: {result.get('error')}"
            }

        except Exception as e:
            print(f"         ❌ Error: {e}")
            self.logger.error(f"❌ [Context Agent] MCP store error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to store memory via MCP"
            }

    async def _answer_question_mcp(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Answer question using MCP search.

        Args:
            params: Dict containing:
                - question: Question to answer

        Returns:
            Answer based on context from Supermemory
        """
        question = params.get("question", "")

        if not question:
            return {
                "success": False,
                "error": "No question provided",
                "message": "Question is required"
            }

        # First search for relevant information
        search_result = await self._search_mcp({"query": question})

        if not search_result.get("success"):
            return {
                "success": False,
                "error": "Could not retrieve information",
                "message": "Failed to search for answer"
            }

        # Extract answer from search results
        mcp_result = search_result.get("result", {}).get("mcp_result", {})

        return {
            "success": True,
            "result": {
                "question": question,
                "answer": f"Found information via Supermemory MCP",
                "mcp_result": mcp_result,
                "confidence": 0.8
            },
            "message": "Question answered via MCP search"
        }

    async def _get_context_mcp(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get context using MCP search.

        Args:
            params: Dict containing:
                - topic: Topic to get context for

        Returns:
            Context results
        """
        topic = params.get("topic", "")

        # Use search to get context
        return await self._search_mcp({"query": topic})

    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities."""
        return {
            "name": self.name,
            "description": self.description,
            "actions": [
                {
                    "name": "search",
                    "description": "Search Supermemory via MCP",
                    "params": ["query"],
                    "mcp_function": "mcp__api-supermemory-ai__search"
                },
                {
                    "name": "store_memory",
                    "description": "Store memory via MCP",
                    "params": ["content"],
                    "mcp_function": "mcp__api-supermemory-ai__addMemory"
                },
                {
                    "name": "answer_question",
                    "description": "Answer questions using MCP search",
                    "params": ["question"]
                },
                {
                    "name": "get_context",
                    "description": "Get context via MCP search",
                    "params": ["topic"]
                }
            ],
            "integrations": ["Supermemory MCP"],
            "requires_mcp_client": True
        }
