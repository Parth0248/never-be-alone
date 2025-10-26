"""Main orchestrator service that coordinates between ASI:One and specialized agents."""
import logging
from typing import Dict, Any, List, Optional
import asyncio
from asi_one_client import ASIOneClient
from asi_one_agentic_client import ASIOneAgenticClient
from agents import TaskClassifierAgent, CalendarAgent
from agents.context_retrieval_agent_mcp import ContextRetrievalAgentMCP
from mcp_client import SupermemoryMCPClient
from reka_client import get_reka_client
from omi_client import OmiClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Main orchestrator that coordinates agent execution."""

    def __init__(self):
        """Initialize orchestrator with Reka, ASI:One clients, Omi client and agents."""
        self.reka = get_reka_client()
        self.asi_one = ASIOneClient()  # For simple intent routing
        self.asi_one_agentic = ASIOneAgenticClient()  # For complex agentic orchestration
        self.omi_client = OmiClient()  # For sending responses to user

        # Initialize MCP client for Supermemory
        self.mcp_client = SupermemoryMCPClient()

        # Initialize specialized agents
        self.agents = {
            "task_classifier": TaskClassifierAgent(),
            "calendar_agent": CalendarAgent(),
            "context_retrieval_agent": ContextRetrievalAgentMCP(mcp_client=self.mcp_client)
        }

        logger.info(f"Orchestrator initialized with Reka.ai + ASI:One (simple + agentic) + Omi + {len(self.agents)} agents")

    async def process_transcription(
        self,
        transcription: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a transcription through the agent orchestration pipeline.

        Args:
            transcription: Text from audio transcription
            context: Additional context (user_id, timestamp, etc.)

        Returns:
            Dict containing:
                - success: bool
                - intent: Detected intent
                - actions_taken: List of actions performed by agents
                - results: Results from each agent
        """
        print(f"\n{'='*80}")
        print(f"ORCHESTRATOR: Starting pipeline...")
        print(f"{'='*80}")
        logger.info(f"[ORCHESTRATOR] Processing transcription: {transcription[:100]}...")

        try:
            # Step 1: Enhance understanding with Reka.ai (non-streaming for testing)
            print(f"\nSTEP 1: Enhancing context with Reka.ai...")
            reka_result = await self.reka.process_text(transcription, context, stream=False)

            if reka_result.get("success"):
                reka_understanding = reka_result.get("reka_response", {})
                print(f"   [OK] Enhanced understanding: {reka_understanding.get('enhanced_understanding', 'N/A')[:80]}...")
                print(f"   [OK] Entities detected: {reka_understanding.get('entities', {})}")
                print(f"   [OK] Intent hints: {reka_understanding.get('intent_hints', [])}")
                logger.info(f"[Reka] Enhanced understanding obtained")
            else:
                print(f"   [WARN] Reka processing failed: {reka_result.get('error')}")
                logger.warning(f"[Reka] Processing failed, continuing without enhancement")
                reka_understanding = {}

            # Step 2: Analyze intent using ASI:One (with Reka's enhancement)
            print(f"\nSTEP 2: Analyzing intent with ASI:One...")

            # Enrich transcription with Reka's understanding
            enriched_text = transcription
            if reka_understanding.get('enhanced_understanding'):
                enriched_text = f"{transcription}\n[Context: {reka_understanding.get('enhanced_understanding')}]"

            intent_analysis = self.asi_one.analyze_intent(enriched_text, context)
            print(f"   [OK] Intent: {intent_analysis.get('intent')}")
            print(f"   [OK] Confidence: {intent_analysis.get('confidence')}")
            print(f"   [OK] Entities: {intent_analysis.get('entities', {})}")
            logger.info(f"[ASI:One] Intent detected: {intent_analysis.get('intent')} "
                       f"(confidence: {intent_analysis.get('confidence')})")

            # Step 3: Route based on complexity (SIMPLE vs COMPLEX)
            print(f"\nSTEP 3: Determining task complexity...")
            is_complex = self.asi_one_agentic.is_complex_task(
                intent_analysis.get("intent", "observation"),
                intent_analysis.get("entities", {})
            )

            results = []
            agentic_response = None

            if is_complex:
                print(f"   [COMPLEX] COMPLEX TASK DETECTED - Routing to ASI:One Agentic Layer")
                logger.info(f"[Routing] Complex task - using ASI:One agentic orchestration")

                # STEP 3A: Process with ASI:One Agentic (with multimodal support)
                print(f"\nSTEP 3A: ASI:One Agentic Orchestration...")

                # Extract images from Reka result if available
                images_base64 = reka_result.get("images_base64", [])

                # Get conversation ID from context
                conv_id = context.get("uid") if context else None

                agentic_result = self.asi_one_agentic.process_complex_task(
                    text=enriched_text,
                    images_base64=images_base64,
                    entities=intent_analysis.get("entities"),
                    intent=intent_analysis.get("intent"),
                    reka_understanding=reka_understanding,
                    context=context,
                    conversation_id=conv_id
                )

                if agentic_result.get("success"):
                    agentic_response = agentic_result.get("response", "")
                    print(f"   [OK] ASI:One Agentic Response: {agentic_response[:100]}...")
                    print(f"   [OK] Model used: {agentic_result.get('model_used')}")
                    print(f"   [OK] Complexity: {agentic_result.get('complexity_score')}/10")
                    print(f"   [OK] Agents used: {', '.join(agentic_result.get('agents_used', ['none']))}")

                    # Check if we need to poll for async results
                    if agentic_result.get("requires_polling"):
                        print(f"   [POLLING] Agent is processing asynchronously, polling for results...")
                        final_response = self.asi_one_agentic.poll_for_agent_result(
                            conversation_id=agentic_result.get("conversation_id"),
                            max_attempts=24,
                            wait_seconds=5
                        )
                        if final_response:
                            agentic_response = final_response
                            print(f"   [OK] Final response received: {agentic_response[:100]}...")

                    # STEP 3B: Send response to user via Omi client
                    print(f"\nSTEP 3B: Sending response to user via Omi...")
                    await self._send_to_omi(agentic_response, transcription, context)

                    results = [{
                        "agent_type": "asi_one_agentic",
                        "action": "complex_orchestration",
                        "success": True,
                        "message": f"Orchestrated via {agentic_result.get('model_used')}",
                        "response": agentic_response,
                        "agents_used": agentic_result.get("agents_used", [])
                    }]
                else:
                    print(f"   [ERROR] ASI:One Agentic failed: {agentic_result.get('error')}")
                    logger.error(f"[ASI:One Agentic] Processing failed: {agentic_result.get('error')}")
                    # Fall back to simple agent routing
                    is_complex = False

            if not is_complex:
                print(f"   [SIMPLE] SIMPLE TASK - Using direct agent routing")
                logger.info(f"[Routing] Simple task - using direct agent execution")

                # Step 3C: Get agent routing from ASI:One (simple mode)
                print(f"\nSTEP 3C: Routing to specialized agents...")
                agent_tasks = self.asi_one.route_to_agents(
                    text=enriched_text,
                    intent=intent_analysis.get("intent"),
                    entities=intent_analysis.get("entities", {}),
                    context=context
                )
                print(f"   [OK] Routing to {len(agent_tasks)} agent(s)")
                for task in agent_tasks:
                    print(f"      - {task.get('agent_type')}: {task.get('action')}")

                # Step 4: Execute agent tasks
                print(f"\nSTEP 4: Executing agent tasks...")
                results = await self._execute_agent_tasks(agent_tasks)
                print(f"   [OK] Completed {len(results)} agent tasks")

                # STEP 4A: Send simple response to user via Omi
                if results and results[0].get("success"):
                    response_text = results[0].get("message", "Task completed")
                    print(f"\nSTEP 4A: Sending response to user via Omi...")
                    await self._send_to_omi(response_text, transcription, context)

            # Step 5: Store everything in Supermemory (with Reka context + ASI:One response)
            print(f"\nSTEP 5: Storing in Supermemory...")
            await self._store_in_supermemory(
                transcription,
                intent_analysis,
                results,
                context,
                reka_understanding,
                agentic_response
            )
            print(f"   [OK] Stored in Supermemory")

            print(f"\n{'='*80}")
            print(f"ORCHESTRATOR: Pipeline complete!")
            print(f"{'='*80}\n")

            return {
                "success": True,
                "transcription": transcription,
                "reka_understanding": reka_understanding,
                "intent": intent_analysis.get("intent"),
                "entities": intent_analysis.get("entities"),
                "confidence": intent_analysis.get("confidence"),
                "agent_tasks": [],  # Not used when agentic layer handles routing
                "results": results,
                "actions_taken": self._summarize_actions(results)
            }

        except Exception as e:
            print(f"\n[ERROR] ORCHESTRATOR ERROR: {e}")
            logger.error(f"[ORCHESTRATOR] Error processing transcription: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "transcription": transcription
            }

    async def _execute_agent_tasks(
        self,
        agent_tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Execute tasks across multiple agents.

        Args:
            agent_tasks: List of agent tasks from ASI:One routing

        Returns:
            List of results from each agent
        """
        results = []

        for idx, task in enumerate(agent_tasks, 1):
            agent_type = task.get("agent_type")
            action = task.get("action")
            params = task.get("params", {})

            print(f"\n   [AGENT {idx}/{len(agent_tasks)}] {agent_type}.{action}")

            # Get the agent
            agent = self.agents.get(agent_type)

            if not agent:
                print(f"      [ERROR] Agent not found: {agent_type}")
                logger.warning(f"❌ [Agent] Agent '{agent_type}' not found, skipping task")
                results.append({
                    "agent_type": agent_type,
                    "success": False,
                    "error": f"Agent not found: {agent_type}"
                })
                continue

            # Execute task with retry logic
            try:
                result = await agent.execute_with_retry(action, params)
                result["agent_type"] = agent_type
                result["action"] = action
                results.append(result)

                if result.get("success"):
                    print(f"      [OK] {result.get('message')}")
                    logger.info(f"[Agent] {agent_type} completed {action}: {result.get('message')}")
                else:
                    print(f"      [WARN] {result.get('error')}")
                    logger.warning(f"[Agent] {agent_type} failed {action}: {result.get('error')}")

            except Exception as e:
                print(f"      [ERROR] Error: {e}")
                logger.error(f"❌ [Agent] Error executing {agent_type}.{action}: {e}")
                results.append({
                    "agent_type": agent_type,
                    "action": action,
                    "success": False,
                    "error": str(e)
                })

        return results

    async def _send_to_omi(
        self,
        response_text: str,
        original_transcription: str,
        context: Optional[Dict[str, Any]]
    ):
        """Send response to user via Omi client.

        Args:
            response_text: Response to send to user
            original_transcription: Original user transcription (for context)
            context: Additional context
        """
        try:
            print(f"   [OMI] Sending {len(response_text)} chars to Omi...")

            # Send as conversation (acts as notification in Omi app)
            result = self.omi_client.send_response(
                response_text=response_text,
                original_context=original_transcription
            )

            if result.get("success"):
                print(f"   [OK] Response sent to Omi successfully!")
                logger.info("[Omi] Response sent to user")
            else:
                print(f"   [WARN] Failed to send to Omi: {result.get('error')}")
                logger.warning(f"[Omi] Failed to send response: {result.get('error')}")

        except Exception as e:
            print(f"   [ERROR] Error sending to Omi: {e}")
            logger.error(f"❌ [Omi] Error sending response: {e}")

    async def _store_in_supermemory(
        self,
        transcription: str,
        intent_analysis: Dict[str, Any],
        agent_results: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]],
        reka_understanding: Optional[Dict[str, Any]] = None,
        agentic_response: Optional[str] = None
    ):
        """Store the transcription and results in Supermemory.

        Args:
            transcription: Original transcription
            intent_analysis: Intent analysis from ASI:One
            agent_results: Results from agent execution
            context: Additional context
        """
        try:
            context_agent = self.agents.get("context_retrieval_agent")

            if not context_agent:
                print(f"   [WARN] Context retrieval agent not available")
                logger.warning("[Supermemory] Context retrieval agent not available")
                return

            # Prepare memory content with Reka enhancement
            memory_content = f"Transcription: {transcription}"

            # Add Reka's enhanced understanding
            if reka_understanding and reka_understanding.get('enhanced_understanding'):
                memory_content += f"\nContext (Reka): {reka_understanding.get('enhanced_understanding')}"

            # Add intent information
            intent = intent_analysis.get("intent", "unknown")
            memory_content += f"\nIntent: {intent}"

            # Add Reka entities
            if reka_understanding and reka_understanding.get('entities'):
                memory_content += f"\nEntities detected: {reka_understanding.get('entities')}"

            # Add action summary
            actions_summary = self._summarize_actions(agent_results)
            if actions_summary:
                memory_content += f"\nActions taken: {', '.join(actions_summary)}"

            # Add ASI:One agentic response if available
            if agentic_response:
                memory_content += f"\nASI:One Agentic Response: {agentic_response[:200]}..."

            print(f"   [MEMORY] Preparing memory content ({len(memory_content)} chars)...")
            print(f"   [MEMORY] Content preview: {memory_content[:100]}...")

            # Store memory
            metadata = {
                "source": "omi_transcription",
                "intent": intent,
                "confidence": intent_analysis.get("confidence", 0),
                "timestamp": context.get("timestamp") if context else None,
                "user_id": context.get("uid") if context else None
            }

            print(f"   [MEMORY] Calling context agent to store memory...")
            result = await context_agent.handle_task("store_memory", {
                "content": memory_content,
                "metadata": metadata
            })

            if result.get("success"):
                print(f"   [OK] Memory stored in Supermemory!")
                logger.info("[Supermemory] Transcription stored successfully")
            else:
                print(f"   [WARN] Storage failed: {result.get('error')}")
                logger.warning(f"[Supermemory] Storage failed: {result.get('error')}")

        except Exception as e:
            print(f"   [ERROR] Error storing in Supermemory: {e}")
            logger.error(f"❌ [Supermemory] Error storing: {e}")

    def _summarize_actions(self, results: List[Dict[str, Any]]) -> List[str]:
        """Summarize actions taken by agents.

        Args:
            results: Agent results

        Returns:
            List of action descriptions
        """
        actions = []

        for result in results:
            if result.get("success"):
                agent_type = result.get("agent_type", "unknown")
                action = result.get("action", "unknown")
                message = result.get("message", "")

                actions.append(f"{agent_type}: {message}")

        return actions

    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents.

        Returns:
            Dict with agent status information
        """
        agent_info = {}

        for name, agent in self.agents.items():
            capabilities = agent.get_capabilities()
            agent_info[name] = {
                "name": capabilities.get("name"),
                "description": capabilities.get("description"),
                "actions": [a.get("name") for a in capabilities.get("actions", [])],
                "status": "active"
            }

        return {
            "total_agents": len(self.agents),
            "agents": agent_info,
            "asi_one_status": "connected" if self.asi_one else "disconnected"
        }

    async def test_agent(self, agent_type: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Test a specific agent action.

        Args:
            agent_type: Type of agent to test
            action: Action to perform
            params: Parameters for the action

        Returns:
            Test result
        """
        agent = self.agents.get(agent_type)

        if not agent:
            return {
                "success": False,
                "error": f"Agent not found: {agent_type}"
            }

        try:
            result = await agent.handle_task(action, params)
            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
_orchestrator_instance = None


def get_orchestrator() -> AgentOrchestrator:
    """Get or create orchestrator singleton instance.

    Returns:
        AgentOrchestrator instance
    """
    global _orchestrator_instance

    if _orchestrator_instance is None:
        _orchestrator_instance = AgentOrchestrator()

    return _orchestrator_instance
