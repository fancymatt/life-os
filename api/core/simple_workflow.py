"""
Simple Workflow Engine - Sequential workflow execution

This is a minimal implementation for the story workflow prototype.
Will be replaced by comprehensive workflow engine in Phase 2.
"""

import time
import uuid
from datetime import datetime
from typing import List, Dict, Any, Callable, Optional
from pydantic import BaseModel
from enum import Enum

from api.core.simple_agent import Agent


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowStep(BaseModel):
    """Definition of a single workflow step"""
    step_id: str
    agent_id: str
    description: str
    inputs: List[str]  # Variable names from context
    outputs: List[str]  # Variable names to store in context


class WorkflowDefinition(BaseModel):
    """Definition of a complete workflow"""
    workflow_id: str
    name: str
    description: str
    version: str = "1.0.0"
    steps: List[WorkflowStep]
    parameters: Dict[str, Any] = {}


class WorkflowExecution(BaseModel):
    """Execution state of a workflow"""
    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    current_step: Optional[str] = None
    steps_completed: int = 0
    steps_total: int
    progress: float = 0.0
    context: Dict[str, Any] = {}  # Shared data between steps
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = None


class SimpleWorkflow:
    """
    Simple sequential workflow executor

    Executes workflow steps in order, passing data through shared context.
    """

    def __init__(
        self,
        definition: WorkflowDefinition,
        agents: Dict[str, Agent],
        progress_callback: Optional[Callable[[int, str, str], None]] = None
    ):
        """
        Initialize workflow

        Args:
            definition: Workflow definition
            agents: Map of agent_id -> Agent instance
            progress_callback: Optional callback for progress updates (step_num, step_name, message)
        """
        self.definition = definition
        self.agents = agents
        self.progress_callback = progress_callback

    async def execute(self, input_params: Dict[str, Any]) -> WorkflowExecution:
        """
        Execute workflow with given parameters

        Args:
            input_params: Input parameters for workflow

        Returns:
            WorkflowExecution with results
        """
        # Create execution record
        execution_id = f"wf_{uuid.uuid4().hex[:12]}"
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=self.definition.workflow_id,
            status=WorkflowStatus.RUNNING,
            steps_total=len(self.definition.steps),
            context=input_params.copy(),
            started_at=datetime.now()
        )

        start_time = time.time()

        try:
            # Execute each step sequentially
            for i, step in enumerate(self.definition.steps):
                execution.current_step = step.step_id
                execution.progress = i / len(self.definition.steps)

                # Report progress if callback provided
                if self.progress_callback:
                    self.progress_callback(i + 1, step.step_id, step.description)

                # Get agent
                agent = self.agents.get(step.agent_id)
                if not agent:
                    raise ValueError(f"Agent not found: {step.agent_id}")

                # Prepare step input from context
                step_input = {
                    key: execution.context.get(key)
                    for key in step.inputs
                    if key in execution.context
                }

                # Execute agent
                step_result = await agent.execute(step_input)

                # Store outputs in context
                for j, output_key in enumerate(step.outputs):
                    if output_key in step_result:
                        execution.context[output_key] = step_result[output_key]
                    elif len(step.outputs) == 1 and len(step_result) > 0:
                        # If single output, use first result value
                        execution.context[output_key] = step_result
                    else:
                        # Try to find matching key in result
                        for result_key, result_value in step_result.items():
                            if result_key == output_key or result_key.endswith(output_key):
                                execution.context[output_key] = result_value
                                break

                execution.steps_completed += 1

            # Workflow completed successfully
            execution.status = WorkflowStatus.COMPLETED
            execution.progress = 1.0
            execution.completed_at = datetime.now()
            execution.execution_time = time.time() - start_time

            # Extract final result (last step's output)
            if self.definition.steps:
                last_step = self.definition.steps[-1]
                execution.result = {
                    key: execution.context.get(key)
                    for key in last_step.outputs
                    if key in execution.context
                }

        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error = str(e)
            execution.completed_at = datetime.now()
            execution.execution_time = time.time() - start_time

        return execution
