from typing import Any, Literal
from pydantic import BaseModel, Field

ActionType = Literal[
    'launch_app', 'click', 'double_click', 'move', 'drag', 'type', 'press',
    'hotkey', 'scroll', 'wait', 'screenshot', 'draw_lion', 'finish'
]

class TaskRequest(BaseModel):
    goal: str = Field(min_length=2, max_length=1000)
    confirm_sensitive: bool = False

class Action(BaseModel):
    type: ActionType
    args: dict[str, Any] = Field(default_factory=dict)
    reason: str = ''

class Plan(BaseModel):
    goal: str
    steps: list[Action] = Field(default_factory=list)

class TaskResult(BaseModel):
    task_id: int
    status: str
    message: str
    steps_completed: int
    verified: bool = False
    screenshots: list[str] = Field(default_factory=list)
    trace: list[str] = Field(default_factory=list)
