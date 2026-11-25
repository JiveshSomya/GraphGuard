from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

class Decision(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    REQUIRE_HUMAN_APPROVAL = "REQUIRE_HUMAN_APPROVAL"

class ExecuteRequest(BaseModel):
    instruction: str = Field(min_length=1, max_length=4000)
    agent_permissions: list[str] = Field(default_factory=lambda: ["search", "read"])
    retrieved_content: str = ""
    requested_tools: list[str] = Field(default_factory=list)
    scenario_id: str | None = None

class ToolRequest(BaseModel):
    tool: str
    agent_permissions: list[str] = Field(default_factory=list)
    instruction: str = ""
    retrieved_content: str = ""
    prior_tools: list[str] = Field(default_factory=list)

class ApprovalAction(BaseModel):
    reviewer: str = Field(default="demo-reviewer", min_length=1, max_length=100)
