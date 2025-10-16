"""
Simple Agent - Base class for workflow agents

This is a minimal implementation for the story workflow prototype.
Will be replaced by comprehensive agent framework in Phase 3.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel


class AgentConfig(BaseModel):
    """Agent configuration"""
    agent_id: str
    name: str
    description: str
    version: str = "1.0.0"
    estimated_time_seconds: float = 30.0
    estimated_cost: float = 0.01


class Agent(ABC):
    """Base class for all agents"""

    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or self.get_default_config()

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent task

        Args:
            input_data: Input parameters for the agent

        Returns:
            Output data from agent execution

        Raises:
            ValueError: If input validation fails
            RuntimeError: If execution fails
        """
        pass

    @abstractmethod
    def get_default_config(self) -> AgentConfig:
        """Return default agent configuration"""
        pass

    def validate_input(self, input_data: Dict[str, Any], required_fields: list) -> None:
        """Validate that required fields are present"""
        missing = [field for field in required_fields if field not in input_data]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
