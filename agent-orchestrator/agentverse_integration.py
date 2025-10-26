"""Integration with Agentverse to discover and use community agents."""
import requests
import logging
from typing import Dict, Any, List, Optional
from config import Config

logger = logging.getLogger(__name__)


class AgentverseClient:
    """Client for interacting with Agentverse API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Agentverse client.

        Args:
            api_key: Agentverse API key
        """
        self.api_key = api_key or Config.AGENTVERSE_API_KEY
        self.base_url = Config.AGENTVERSE_BASE_URL
        self.mcp_url = Config.AGENTVERSE_MCP_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def discover_agents(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Discover available agents in Agentverse marketplace.

        Args:
            category: Filter by category (e.g., "productivity", "communication")
            tags: Filter by tags

        Returns:
            List of available agents
        """
        try:
            params = {}
            if category:
                params["category"] = category
            if tags:
                params["tags"] = ",".join(tags)

            response = requests.get(
                f"{self.base_url}/agents",
                headers=self.headers,
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                return response.json().get("agents", [])
            else:
                logger.warning(f"Agent discovery returned status {response.status_code}")
                return []

        except requests.exceptions.RequestException as e:
            logger.error(f"Error discovering agents: {e}")
            return []

    def get_agent_info(self, agent_address: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific agent.

        Args:
            agent_address: Agent address (e.g., "agent1qw...")

        Returns:
            Agent information or None
        """
        try:
            response = requests.get(
                f"{self.base_url}/agents/{agent_address}",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get agent info: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting agent info: {e}")
            return None

    def find_agents_for_task(self, task_description: str) -> List[Dict[str, Any]]:
        """Find suitable agents for a specific task.

        Args:
            task_description: Description of the task

        Returns:
            List of suitable agents
        """
        # Get all agents
        all_agents = self.discover_agents()

        # Filter based on task description (simple keyword matching)
        task_lower = task_description.lower()

        suitable_agents = []

        for agent in all_agents:
            agent_desc = agent.get("description", "").lower()
            agent_name = agent.get("name", "").lower()
            agent_tags = [t.lower() for t in agent.get("tags", [])]

            # Check if agent matches task
            if any(word in agent_desc or word in agent_name or word in agent_tags
                   for word in task_lower.split()):
                suitable_agents.append(agent)

        return suitable_agents

    def get_recommended_agents(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get recommended agents for common work-life balance tasks.

        Returns:
            Dict of agent categories with recommended agents
        """
        recommendations = {
            "productivity": [],
            "health_wellness": [],
            "communication": [],
            "automation": [],
            "information": []
        }

        # Search for agents in each category
        for category in recommendations.keys():
            agents = self.discover_agents(category=category)
            recommendations[category] = agents[:5]  # Top 5 per category

        return recommendations


# Recommended agent categories for work-life balance
RECOMMENDED_AGENT_TYPES = {
    "productivity": [
        "Task Manager Agent",
        "Time Tracking Agent",
        "Focus Timer Agent",
        "Goal Setting Agent",
        "Habit Tracker Agent"
    ],
    "health_wellness": [
        "Exercise Reminder Agent",
        "Water Intake Agent",
        "Meditation Agent",
        "Sleep Tracker Agent",
        "Nutrition Agent"
    ],
    "communication": [
        "Email Manager Agent",
        "Meeting Scheduler Agent",
        "Message Summarizer Agent",
        "Contact Manager Agent"
    ],
    "automation": [
        "File Organizer Agent",
        "Backup Agent",
        "Report Generator Agent",
        "Data Sync Agent"
    ],
    "information": [
        "News Aggregator Agent",
        "Weather Agent",
        "Calendar Sync Agent",
        "Knowledge Base Agent"
    ]
}


def print_agent_recommendations():
    """Print recommended agent types for work-life balance."""
    print("\n" + "="*80)
    print("Recommended Agents for Work-Life Balance")
    print("="*80 + "\n")

    for category, agents in RECOMMENDED_AGENT_TYPES.items():
        print(f"\n{category.upper().replace('_', ' ')}")
        print("-" * 40)

        for agent in agents:
            print(f"  • {agent}")

    print("\n" + "="*80 + "\n")


def discover_and_save_agents():
    """Discover agents from Agentverse and save recommendations."""
    client = AgentverseClient()

    print("\n" + "="*80)
    print("Discovering Agents from Agentverse")
    print("="*80 + "\n")

    recommendations = client.get_recommended_agents()

    for category, agents in recommendations.items():
        if agents:
            print(f"\n{category.upper().replace('_', ' ')} ({len(agents)} found)")
            print("-" * 40)

            for agent in agents:
                name = agent.get("name", "Unknown")
                description = agent.get("description", "No description")
                address = agent.get("address", "N/A")

                print(f"\n  Name: {name}")
                print(f"  Description: {description}")
                print(f"  Address: {address}")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "discover":
            discover_and_save_agents()
        elif command == "recommend":
            print_agent_recommendations()
        elif command == "search":
            if len(sys.argv) < 3:
                print("Usage: python agentverse_integration.py search <task_description>")
                sys.exit(1)

            task = " ".join(sys.argv[2:])
            client = AgentverseClient()
            agents = client.find_agents_for_task(task)

            print(f"\nFound {len(agents)} agents for task: {task}\n")

            for agent in agents:
                print(f"  • {agent.get('name')}: {agent.get('description')}")

            print()
        else:
            print(f"Unknown command: {command}")
    else:
        print("Usage: python agentverse_integration.py <command>")
        print("\nCommands:")
        print("  discover   - Discover agents from Agentverse")
        print("  recommend  - Show recommended agent types")
        print("  search <task> - Search for agents for a specific task")
