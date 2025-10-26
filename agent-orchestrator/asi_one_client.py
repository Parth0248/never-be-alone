"""ASI:One API Client for intent routing and orchestration."""
import requests
import logging
import uuid
from typing import Dict, List, Any, Optional
from config import Config

logger = logging.getLogger(__name__)


class ASIOneClient:
    """Client for interacting with ASI:One Agentic API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize ASI:One client.

        Args:
            api_key: ASI:One API key (defaults to Config.ASI_ONE_API_KEY)
        """
        self.api_key = api_key or Config.ASI_ONE_API_KEY
        self.base_url = "https://api.asi1.ai/v1"
        self.model = "asi1-fast-agentic"  # Ultra-fast for real-time responses
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def analyze_intent(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze text using ASI:One Agentic model to determine user intent.

        Args:
            text: Text to analyze (transcription)
            context: Additional context (user_id, timestamp, location, etc.)

        Returns:
            Dict containing:
                - intent: Primary intent (e.g., "create_reminder", "search_info")
                - confidence: Confidence score (0-1)
                - entities: Extracted entities (people, dates, actions, etc.)
                - suggested_agents: List of agent types to handle this
                - agent_calls: Agent discovery results from ASI:One
        """
        # Build context-aware prompt
        context_str = ""
        if context:
            context_str = f"\nContext: {context}"

        system_prompt = """You are an intent classifier for a personal AI assistant.
Analyze the user's request and identify:
1. Primary intent (create_reminder, search_info, send_communication, smart_home_control, or observation)
2. Entities (people, times, actions, locations, objects)
3. Confidence level (0-1)
4. Required agents to fulfill the request

Available agent types:
- task_classifier: Analyzes and categorizes requests
- calendar_agent: Creates reminders and events
- context_retrieval_agent: Searches memories and answers questions
- communication_agent: Sends messages
- smart_home_agent: Controls devices

Return your analysis as structured data."""

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{text}{context_str}"}
            ],
            "stream": False
        }

        try:
            session_id = str(uuid.uuid4())
            headers = self.headers.copy()
            headers["x-session-id"] = session_id

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=15
            )
            response.raise_for_status()
            result = response.json()

            # Parse ASI:One response
            return self._parse_asi_one_response(result, text)

        except requests.exceptions.RequestException as e:
            logger.error(f"ASI:One API error: {e}")
            # Fallback to simple intent detection
            return self._fallback_intent_detection(text)

    def _parse_asi_one_response(self, result: Dict[str, Any], text: str) -> Dict[str, Any]:
        """Parse ASI:One agentic response into our format.

        Args:
            result: Raw API response
            text: Original text

        Returns:
            Parsed intent analysis
        """
        try:
            # ASI:One returns agent discovery in executable_data
            executable_data = result.get("executable_data", {})
            agent_calls = executable_data.get("agent_calls", [])

            # Extract intent from content or use first agent as hint
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

            # Simple intent mapping from agent calls
            if agent_calls:
                first_agent = agent_calls[0].get("tool_name", "")
                confidence = agent_calls[0].get("confidence", 0.7)
            else:
                first_agent = ""
                confidence = 0.6

            # Map agent names to our intents
            intent = self._map_agent_to_intent(first_agent, text)
            entities = self._extract_entities_from_text(text)

            return {
                "intent": intent,
                "confidence": confidence,
                "entities": entities,
                "suggested_agents": [a.get("tool_name") for a in agent_calls],
                "agent_calls": agent_calls,
                "raw_response": content
            }

        except Exception as e:
            logger.error(f"Error parsing ASI:One response: {e}")
            return self._fallback_intent_detection(text)

    def _map_agent_to_intent(self, agent_name: str, text: str) -> str:
        """Map ASI:One agent name to our intent."""
        text_lower = text.lower()

        if "calendar" in agent_name or "remind" in text_lower:
            return "create_reminder"
        elif "search" in agent_name or any(w in text_lower for w in ["what", "when", "where", "who", "?"]):
            return "search_info"
        elif "message" in agent_name or "communication" in agent_name:
            return "send_communication"
        elif "home" in agent_name or "device" in agent_name:
            return "smart_home_control"
        else:
            return "observation"

    def _extract_entities_from_text(self, text: str) -> Dict[str, Any]:
        """Extract basic entities from text."""
        # Use fallback entity extraction
        return self._extract_reminder_entities(text)

    def route_to_agents(
        self,
        text: str,
        intent: str,
        entities: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Route a request to appropriate agents.

        Uses ASI:One's agent discovery if available, falls back to manual routing.

        Args:
            text: Original text
            intent: Detected intent
            entities: Extracted entities
            context: Additional context

        Returns:
            List of agent tasks to execute
        """
        # If we have agent_calls from analyze_intent, use those
        if entities and "agent_calls" in entities:
            agent_calls = entities.get("agent_calls", [])
            if agent_calls:
                # Convert ASI:One agent calls to our format
                return self._convert_asi_one_agents(agent_calls, text, entities)

        # Fallback to manual routing
        return self._fallback_routing(intent, text, entities)

    def _convert_asi_one_agents(
        self,
        agent_calls: List[Dict[str, Any]],
        text: str,
        entities: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Convert ASI:One agent calls to our agent task format."""
        tasks = []

        for call in agent_calls:
            tool_name = call.get("tool_name", "")
            arguments = call.get("arguments", {})

            # Map to our agent types
            agent_type, action = self._map_tool_to_agent(tool_name, text)

            if agent_type:
                tasks.append({
                    "agent_type": agent_type,
                    "action": action,
                    "params": arguments if arguments else entities
                })

        return tasks if tasks else self._fallback_routing(entities.get("intent", "observation"), text, entities)

    def _map_tool_to_agent(self, tool_name: str, text: str) -> tuple:
        """Map ASI:One tool name to our (agent_type, action)."""
        tool_lower = tool_name.lower()
        text_lower = text.lower()

        if "calendar" in tool_lower or "remind" in text_lower:
            return ("calendar_agent", "create_reminder")
        elif "search" in tool_lower or "memory" in tool_lower:
            return ("context_retrieval_agent", "search")
        elif "message" in tool_lower or "email" in tool_lower:
            return ("communication_agent", "send_message")
        else:
            return ("task_classifier", "classify")

    def _fallback_intent_detection(self, text: str) -> Dict[str, Any]:
        """Fallback intent detection using simple keyword matching.

        This is used when ASI:One API is unavailable.
        """
        text_lower = text.lower()

        # Intent patterns
        if any(word in text_lower for word in ['remind', 'reminder', 'remember to']):
            return {
                "intent": "create_reminder",
                "confidence": 0.8,
                "entities": self._extract_reminder_entities(text),
                "suggested_agents": ["calendar_agent"]
            }

        if any(word in text_lower for word in ['what', 'when', 'where', 'who', '?']):
            return {
                "intent": "search_info",
                "confidence": 0.7,
                "entities": {"query": text},
                "suggested_agents": ["context_retrieval_agent"]
            }

        if any(word in text_lower for word in ['send', 'email', 'message', 'text']):
            return {
                "intent": "send_communication",
                "confidence": 0.75,
                "entities": self._extract_communication_entities(text),
                "suggested_agents": ["communication_agent"]
            }

        if any(word in text_lower for word in ['turn on', 'turn off', 'set', 'lights', 'thermostat']):
            return {
                "intent": "smart_home_control",
                "confidence": 0.8,
                "entities": self._extract_smart_home_entities(text),
                "suggested_agents": ["smart_home_agent"]
            }

        # Default: observation/note
        return {
            "intent": "observation",
            "confidence": 0.6,
            "entities": {"text": text},
            "suggested_agents": ["task_classifier_agent"]
        }

    def _fallback_routing(
        self,
        intent: str,
        text: str,
        entities: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Fallback routing logic when ASI:One is unavailable."""

        routing_map = {
            "create_reminder": [{
                "agent_type": "calendar_agent",
                "action": "create_reminder",
                "params": entities
            }],
            "search_info": [{
                "agent_type": "context_retrieval_agent",
                "action": "search",
                "params": {"query": text}
            }],
            "send_communication": [{
                "agent_type": "communication_agent",
                "action": "send_message",
                "params": entities
            }],
            "smart_home_control": [{
                "agent_type": "smart_home_agent",
                "action": "control_device",
                "params": entities
            }],
            "observation": [{
                "agent_type": "task_classifier_agent",
                "action": "classify",
                "params": {"text": text}
            }]
        }

        return routing_map.get(intent, [{
            "agent_type": "task_classifier_agent",
            "action": "classify",
            "params": {"text": text}
        }])

    def _extract_reminder_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from reminder text."""
        # This is a simple version - in production, use NER models
        entities = {
            "text": text,
            "action": None,
            "time": None,
            "person": None
        }

        # Extract time references
        time_keywords = ['tomorrow', 'today', 'tonight', 'next week', 'monday', 'tuesday']
        for keyword in time_keywords:
            if keyword in text.lower():
                entities["time"] = keyword
                break

        # Extract action
        action_words = ['call', 'email', 'message', 'meet', 'buy', 'send']
        for action in action_words:
            if action in text.lower():
                entities["action"] = action
                break

        return entities

    def _extract_communication_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from communication text."""
        return {
            "text": text,
            "recipient": None,  # Would extract from text
            "message": text,
            "channel": "email"  # Default
        }

    def _extract_smart_home_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from smart home command."""
        text_lower = text.lower()

        command = "turn_on" if "turn on" in text_lower else "turn_off" if "turn off" in text_lower else "set"

        return {
            "command": command,
            "device": None,  # Would extract device name
            "value": None,  # For set commands
            "text": text
        }

    def get_agent_capabilities(self) -> List[Dict[str, Any]]:
        """Get list of available agents and their capabilities from ASI:One."""
        try:
            response = requests.get(
                f"{self.base_url}/agents",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json().get("agents", [])

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching agent capabilities: {e}")
            return []
