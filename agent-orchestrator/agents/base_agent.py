"""Base agent class for all specialized agents."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all specialized agents."""

    def __init__(self, name: str, description: str):
        """Initialize base agent.

        Args:
            name: Agent name
            description: Agent description and capabilities
        """
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"agent.{name}")

    @abstractmethod
    async def handle_task(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a task assigned to this agent.

        Args:
            action: Action to perform
            params: Parameters for the action

        Returns:
            Dict containing:
                - success: bool
                - result: Any result data
                - message: str describing outcome
                - error: Optional error message
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities and supported actions.

        Returns:
            Dict describing agent capabilities
        """
        pass

    def log_task(self, action: str, params: Dict[str, Any], result: Dict[str, Any]):
        """Log task execution for monitoring and debugging.

        Args:
            action: Action performed
            params: Parameters used
            result: Result of execution
        """
        self.logger.info(
            f"Task executed: {action}",
            extra={
                "agent": self.name,
                "action": action,
                "params": params,
                "success": result.get("success", False)
            }
        )

    async def execute_with_retry(
        self,
        action: str,
        params: Dict[str, Any],
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """Execute task with retry logic.

        Args:
            action: Action to perform
            params: Parameters
            max_retries: Maximum number of retries

        Returns:
            Task result
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                result = await self.handle_task(action, params)
                self.log_task(action, params, result)
                return result

            except Exception as e:
                last_error = str(e)
                self.logger.warning(
                    f"Attempt {attempt + 1}/{max_retries} failed: {e}"
                )

                if attempt == max_retries - 1:
                    break

        return {
            "success": False,
            "error": f"Failed after {max_retries} attempts: {last_error}",
            "message": "Task execution failed"
        }
