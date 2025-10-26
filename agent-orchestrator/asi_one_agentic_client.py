"""
ASI:One Agentic Client - Enhanced version with multimodal support and dynamic model selection.
Handles complex tasks that require multi-agent orchestration from Agentverse marketplace.
"""
import requests
import logging
import uuid
import time
import json
from typing import Dict, List, Any, Optional, Literal
from config import Config

logger = logging.getLogger(__name__)

ModelType = Literal["asi1-fast-agentic", "asi1-agentic", "asi1-extended-agentic"]


class ASIOneAgenticClient:
    """Enhanced ASI:One client for complex agentic orchestration with multimodal support."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize ASI:One agentic client.

        Args:
            api_key: ASI:One API key (defaults to Config.ASI_ONE_API_KEY)
        """
        self.api_key = api_key or Config.ASI_ONE_API_KEY
        self.base_url = "https://api.asi1.ai/v1"
        self.default_model = "asi1-agentic"  # Balanced model for complex tasks
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.session_map: Dict[str, str] = {}  # conversation_id -> session_id mapping

    def select_model(self, complexity_score: int, multi_agent: bool = False) -> ModelType:
        """Dynamically select ASI:One model based on task complexity.

        Args:
            complexity_score: Complexity score (1-10)
                1-3: Simple tasks (fast model)
                4-7: Moderate complexity (balanced model)
                8-10: Complex multi-stage (extended model)
            multi_agent: If True and score >= 6, upgrade to extended model

        Returns:
            Model name to use
        """
        if complexity_score <= 3:
            return "asi1-fast-agentic"
        elif complexity_score <= 7 and not multi_agent:
            return "asi1-agentic"
        else:
            # Complex multi-agent workflows need extended context
            return "asi1-extended-agentic"

    def calculate_complexity(
        self,
        text: str,
        entities: Dict[str, Any],
        intent: str,
        reka_understanding: Optional[Dict[str, Any]] = None
    ) -> int:
        """Calculate task complexity score (1-10).

        Args:
            text: Input text
            entities: Extracted entities
            intent: Detected intent
            reka_understanding: Enhanced understanding from Reka

        Returns:
            Complexity score (1-10)
        """
        score = 1

        # Base complexity from intent
        intent_complexity = {
            "observation": 1,
            "search_info": 2,
            "send_communication": 4,
            "create_reminder": 5,
            "smart_home_control": 5,
            "multi_step_orchestration": 9,
            "complex_scheduling": 8,
            "travel_planning": 9,
            "workflow_automation": 10
        }
        score = intent_complexity.get(intent, 3)

        # Add complexity from entities
        entity_count = len(entities)
        if entity_count > 5:
            score += 2
        elif entity_count > 2:
            score += 1

        # Add complexity from text length (longer = more complex)
        word_count = len(text.split())
        if word_count > 50:
            score += 2
        elif word_count > 20:
            score += 1

        # Add complexity if Reka detected multiple entities or complex context
        if reka_understanding:
            reka_entities = reka_understanding.get("entities", {})
            if len(reka_entities) > 3:
                score += 1

            # Check for temporal complexity (multiple time references)
            if any(key in str(reka_entities).lower() for key in ["tomorrow", "next week", "schedule", "calendar"]):
                score += 1

        # Cap at 10
        return min(score, 10)

    def get_or_create_session(self, conversation_id: str) -> str:
        """Get existing session ID or create new one for conversation.

        Args:
            conversation_id: Unique conversation identifier

        Returns:
            Session UUID for ASI:One API
        """
        if conversation_id not in self.session_map:
            self.session_map[conversation_id] = str(uuid.uuid4())
            logger.info(f"Created new ASI:One session: {self.session_map[conversation_id]}")

        return self.session_map[conversation_id]

    def process_complex_task(
        self,
        text: str,
        images_base64: Optional[List[str]] = None,
        entities: Optional[Dict[str, Any]] = None,
        intent: Optional[str] = None,
        reka_understanding: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[str] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Process a complex task using ASI:One agentic models.

        Args:
            text: Input text (can be enhanced prompt from Reka)
            images_base64: Optional list of base64-encoded images
            entities: Extracted entities
            intent: Detected intent
            reka_understanding: Enhanced understanding from Reka
            context: Additional context
            conversation_id: Conversation ID for session management
            stream: Whether to stream response

        Returns:
            Dict containing:
                - success: bool
                - response: Agent response text
                - agents_used: List of Agentverse agents that were called
                - model_used: Which ASI:One model was used
                - session_id: Session ID for follow-up
                - requires_polling: Whether to poll for async results
        """
        try:
            # Calculate complexity and select model
            complexity = self.calculate_complexity(
                text,
                entities or {},
                intent or "observation",
                reka_understanding
            )

            # Check if this is multi-agent task
            is_multi_agent = complexity >= 6 or (
                intent in ["multi_step_orchestration", "travel_planning", "complex_scheduling", "workflow_automation"]
            )

            model = self.select_model(complexity, is_multi_agent)

            logger.info(f"📊 Task complexity: {complexity}/10, Multi-agent: {is_multi_agent}, Model: {model}")

            # Build multimodal content
            content = []

            # Add images first (if provided)
            if images_base64:
                for img_base64 in images_base64:
                    content.append({
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{img_base64}"
                    })
                logger.info(f"📸 Added {len(images_base64)} images to ASI:One request")

            # Build enhanced text prompt
            prompt_parts = []

            # Add Reka's understanding if available
            if reka_understanding and reka_understanding.get("enhanced_understanding"):
                prompt_parts.append(f"**Context from Vision/Audio Analysis:**\n{reka_understanding['enhanced_understanding']}")

            if reka_understanding and reka_understanding.get("entities"):
                prompt_parts.append(f"\n**Detected Entities:**\n{json.dumps(reka_understanding['entities'], indent=2)}")

            # Add the main text
            prompt_parts.append(f"\n**User Request:**\n{text}")

            # Add task instruction for ASI:One
            prompt_parts.append(
                "\n**Instructions:**\n"
                "You are an intelligent AI orchestrator with access to Agentverse marketplace agents. "
                "Based on the user's request and context provided:\n"
                "1. Identify what the user needs (scheduling, reminders, booking, information, etc.)\n"
                "2. Discover and coordinate with relevant agents from Agentverse marketplace\n"
                "3. Execute the required workflow autonomously\n"
                "4. Provide a clear, actionable response to the user\n\n"
                "If this requires multiple steps or agents, coordinate them automatically and report back when complete."
            )

            # Add text content
            content.append({
                "type": "text",
                "text": "\n".join(prompt_parts)
            })

            # Get or create session
            conv_id = conversation_id or str(uuid.uuid4())
            session_id = self.get_or_create_session(conv_id)

            # Build request
            headers = self.headers.copy()
            headers["x-session-id"] = session_id

            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                "stream": stream
            }

            logger.info(f"🚀 Calling ASI:One {model} with session {session_id[:8]}...")

            # Make request (non-streaming for now)
            if not stream:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=90
                )
                response.raise_for_status()
                result = response.json()

                # Parse response
                assistant_message = result.get("choices", [{}])[0].get("message", {}).get("content", "")

                # Check if this is a deferred response (agent still processing)
                is_deferred = "I've sent the message" in assistant_message or "waiting for" in assistant_message.lower()

                # Extract agent calls if available
                executable_data = result.get("executable_data", {})
                # Handle both dict and list formats
                if isinstance(executable_data, dict):
                    agent_calls = executable_data.get("agent_calls", [])
                elif isinstance(executable_data, list):
                    agent_calls = executable_data
                else:
                    agent_calls = []

                agents_used = [call.get("tool_name", "unknown") for call in agent_calls if isinstance(call, dict)]

                logger.info(f"✅ ASI:One response received ({len(assistant_message)} chars)")
                if agents_used:
                    logger.info(f"🤖 Agents used: {', '.join(agents_used)}")

                return {
                    "success": True,
                    "response": assistant_message,
                    "agents_used": agents_used,
                    "model_used": model,
                    "complexity_score": complexity,
                    "session_id": session_id,
                    "conversation_id": conv_id,
                    "requires_polling": is_deferred,
                    "raw_result": result
                }

            else:
                # Streaming not implemented yet
                return {
                    "success": False,
                    "error": "Streaming not yet implemented for agentic client"
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ ASI:One API error: {e}")
            return {
                "success": False,
                "error": f"ASI:One API error: {str(e)}",
                "model_used": model if 'model' in locals() else "unknown"
            }
        except Exception as e:
            logger.error(f"❌ Unexpected error in ASI:One agentic client: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }

    def poll_for_agent_result(
        self,
        conversation_id: str,
        max_attempts: int = 24,
        wait_seconds: int = 5
    ) -> Optional[str]:
        """Poll for async agent results from Agentverse.

        Args:
            conversation_id: Conversation ID to poll
            max_attempts: Maximum polling attempts (default: 24 = ~2 minutes)
            wait_seconds: Seconds to wait between polls (default: 5)

        Returns:
            Final response text or None if timeout
        """
        session_id = self.session_map.get(conversation_id)
        if not session_id:
            logger.error("❌ No session found for conversation ID")
            return None

        headers = self.headers.copy()
        headers["x-session-id"] = session_id

        # Get the last message to compare against
        last_content = None

        logger.info(f"🔄 Starting polling for agent results (max {max_attempts} attempts, {wait_seconds}s interval)...")

        for attempt in range(max_attempts):
            time.sleep(wait_seconds)

            try:
                # Send "Any update?" message
                payload = {
                    "model": "asi1-agentic",
                    "messages": [
                        {
                            "role": "user",
                            "content": "Any update?"
                        }
                    ],
                    "stream": False
                }

                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()

                current_content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

                logger.info(f"🔄 Poll attempt {attempt + 1}/{max_attempts}: {len(current_content)} chars")

                # Check if content has changed
                if last_content and current_content != last_content:
                    # Content changed - agent finished!
                    logger.info(f"✅ Agent completed! New response received.")
                    return current_content

                last_content = current_content

            except Exception as e:
                logger.warning(f"⚠️  Poll attempt {attempt + 1} failed: {e}")

        logger.warning(f"⏰ Polling timeout after {max_attempts} attempts")
        return None

    def is_complex_task(self, intent: str, entities: Dict[str, Any]) -> bool:
        """Determine if a task requires ASI:One agentic orchestration.

        Args:
            intent: Detected intent
            entities: Extracted entities

        Returns:
            True if task is complex enough to warrant agentic orchestration
        """
        # Complex intents that always need agentic layer
        complex_intents = {
            "multi_step_orchestration",
            "complex_scheduling",
            "travel_planning",
            "workflow_automation",
            "create_reminder",  # Reminders need calendar agents
            "smart_home_control"  # Smart home needs device agents
        }

        if intent in complex_intents:
            return True

        # Check for temporal complexity (multiple time references)
        entity_values = str(entities).lower()
        time_indicators = ["tomorrow", "next week", "schedule", "remind", "calendar", "meeting", "appointment"]
        if any(indicator in entity_values for indicator in time_indicators):
            return True

        # Check for action sequences
        action_indicators = ["then", "after", "and then", "followed by", "next"]
        if any(indicator in entity_values for indicator in action_indicators):
            return True

        return False
