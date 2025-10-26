"""Task Classification Agent - Analyzes and categorizes transcriptions."""
from typing import Dict, Any
import re
from datetime import datetime
from .base_agent import BaseAgent


class TaskClassifierAgent(BaseAgent):
    """Agent that classifies transcriptions and extracts structured information."""

    def __init__(self):
        super().__init__(
            name="task_classifier",
            description="Analyzes transcriptions to identify intents, extract entities, and categorize requests"
        )

    async def handle_task(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle classification tasks.

        Args:
            action: Action to perform (classify, extract_entities, categorize)
            params: Parameters including 'text' to analyze

        Returns:
            Classification result
        """
        text = params.get("text", "")

        if action == "classify":
            return await self._classify_text(text, params)
        elif action == "extract_entities":
            return await self._extract_entities(text)
        elif action == "categorize":
            return await self._categorize(text)
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}",
                "message": "Action not supported"
            }

    async def _classify_text(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Classify text into categories with intent and entities.

        Args:
            text: Text to classify
            context: Additional context

        Returns:
            Classification result
        """
        text_lower = text.lower()

        # Determine category
        category = self._determine_category(text_lower)

        # Extract intent
        intent = self._extract_intent(text_lower, category)

        # Extract entities
        entities = await self._extract_entities(text)

        # Determine urgency
        urgency = self._determine_urgency(text_lower)

        # Determine if action is required
        requires_action = self._requires_action(category, intent)

        return {
            "success": True,
            "result": {
                "category": category,
                "intent": intent,
                "entities": entities["result"],
                "urgency": urgency,
                "requires_action": requires_action,
                "original_text": text,
                "confidence": 0.85  # Would use ML model in production
            },
            "message": f"Classified as {category} with intent {intent}"
        }

    def _determine_category(self, text: str) -> str:
        """Determine the category of the text.

        Categories:
        - command: Direct instruction to do something
        - question: Asking for information
        - reminder: Setting up a reminder
        - observation: General statement/note
        - communication: Sending a message
        - smart_home: Controlling devices
        """
        if any(word in text for word in ['remind', 'reminder', 'remember to', 'don\'t forget']):
            return "reminder"

        if any(word in text for word in ['what', 'when', 'where', 'who', 'how', 'why', '?']):
            return "question"

        if any(word in text for word in ['send', 'email', 'message', 'text', 'call']):
            return "communication"

        if any(word in text for word in ['turn on', 'turn off', 'set', 'adjust', 'lights', 'thermostat', 'temperature']):
            return "smart_home"

        if any(word in text for word in ['do', 'make', 'create', 'schedule', 'book', 'order']):
            return "command"

        return "observation"

    def _extract_intent(self, text: str, category: str) -> str:
        """Extract specific intent based on category."""

        intent_map = {
            "reminder": "create_reminder",
            "question": "search_information",
            "communication": "send_message",
            "smart_home": "control_device",
            "command": "execute_action",
            "observation": "store_context"
        }

        # More specific intents based on keywords
        if "meeting" in text or "schedule" in text:
            return "schedule_event"
        if "weather" in text:
            return "get_weather"
        if "news" in text:
            return "get_news"

        return intent_map.get(category, "unknown")

    async def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from text.

        Entities include:
        - time: Time references (tomorrow, 3pm, next week)
        - person: People mentioned
        - location: Places mentioned
        - action: Actions to perform
        - object: Objects/things mentioned
        """
        entities = {
            "time": self._extract_time_references(text),
            "person": self._extract_people(text),
            "location": self._extract_locations(text),
            "action": self._extract_actions(text),
            "object": self._extract_objects(text)
        }

        return {
            "success": True,
            "result": entities,
            "message": "Entities extracted"
        }

    def _extract_time_references(self, text: str) -> list:
        """Extract time references from text."""
        time_patterns = [
            r'\d{1,2}:\d{2}\s*(am|pm)?',  # 3:00, 3:00pm
            r'\d{1,2}\s*(am|pm)',  # 3pm
            r'tomorrow',
            r'today',
            r'tonight',
            r'next\s+week',
            r'next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'in\s+\d+\s+(minutes?|hours?|days?|weeks?)',
        ]

        times = []
        text_lower = text.lower()

        for pattern in time_patterns:
            matches = re.findall(pattern, text_lower)
            times.extend(matches)

        return times

    def _extract_people(self, text: str) -> list:
        """Extract people/names from text."""
        # Simple pattern - would use NER in production
        people_patterns = [
            r'\bmom\b',
            r'\bdad\b',
            r'\b[A-Z][a-z]+\b',  # Capitalized words (names)
        ]

        people = []
        for pattern in people_patterns:
            matches = re.findall(pattern, text)
            people.extend(matches)

        return list(set(people))  # Remove duplicates

    def _extract_locations(self, text: str) -> list:
        """Extract locations from text."""
        location_keywords = ['home', 'office', 'work', 'store', 'gym', 'restaurant']
        locations = []

        text_lower = text.lower()
        for location in location_keywords:
            if location in text_lower:
                locations.append(location)

        return locations

    def _extract_actions(self, text: str) -> list:
        """Extract action verbs from text."""
        action_verbs = [
            'call', 'email', 'send', 'message', 'text', 'meet', 'schedule',
            'buy', 'order', 'book', 'reserve', 'turn on', 'turn off',
            'set', 'adjust', 'create', 'make', 'do', 'get', 'check'
        ]

        actions = []
        text_lower = text.lower()

        for action in action_verbs:
            if action in text_lower:
                actions.append(action)

        return actions

    def _extract_objects(self, text: str) -> list:
        """Extract objects/things mentioned in text."""
        # Simple keyword extraction - would use NER in production
        common_objects = [
            'lights', 'thermostat', 'door', 'window', 'tv', 'music',
            'alarm', 'reminder', 'calendar', 'email', 'message'
        ]

        objects = []
        text_lower = text.lower()

        for obj in common_objects:
            if obj in text_lower:
                objects.append(obj)

        return objects

    def _determine_urgency(self, text: str) -> str:
        """Determine urgency level of the request.

        Returns: 'high', 'medium', 'low'
        """
        urgent_keywords = ['urgent', 'asap', 'immediately', 'now', 'right now', 'emergency']
        high_priority_keywords = ['important', 'critical', 'soon', 'today', 'tonight']

        if any(keyword in text for keyword in urgent_keywords):
            return "high"

        if any(keyword in text for keyword in high_priority_keywords):
            return "medium"

        return "low"

    def _requires_action(self, category: str, intent: str) -> bool:
        """Determine if the classification requires agent action.

        Args:
            category: Text category
            intent: Extracted intent

        Returns:
            True if action is required
        """
        action_categories = ["command", "reminder", "communication", "smart_home"]
        return category in action_categories

    async def _categorize(self, text: str) -> Dict[str, Any]:
        """Simple categorization without full analysis.

        Args:
            text: Text to categorize

        Returns:
            Category information
        """
        category = self._determine_category(text.lower())

        return {
            "success": True,
            "result": {
                "category": category,
                "text": text
            },
            "message": f"Categorized as {category}"
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities."""
        return {
            "name": self.name,
            "description": self.description,
            "actions": [
                {
                    "name": "classify",
                    "description": "Fully classify text with intent and entities",
                    "params": ["text"]
                },
                {
                    "name": "extract_entities",
                    "description": "Extract structured entities from text",
                    "params": ["text"]
                },
                {
                    "name": "categorize",
                    "description": "Simple categorization of text",
                    "params": ["text"]
                }
            ],
            "categories": [
                "command", "question", "reminder", "observation",
                "communication", "smart_home"
            ]
        }
