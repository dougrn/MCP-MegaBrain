"""Pydantic data models for MegaBrain memory structures."""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


def current_iso_time() -> str:
    """Return the current UTC time as an ISO string."""
    return datetime.now(timezone.utc).isoformat()


class Rule(BaseModel):
    """A hard rule or architectural constraint."""
    id: Optional[int] = None
    project: str = Field(default="global", description="Project identifier or 'global'")
    category: str = Field(default="general", description="Category: language, architecture, security, git, etc.")
    rule: str = Field(description="The constraint or rule statement")
    severity: str = Field(default="CRITICAL", description="Severity: CRITICAL, HIGH, MEDIUM, LOW")
    created_at: str = Field(default_factory=current_iso_time)
    updated_at: str = Field(default_factory=current_iso_time)


class MandatorySpec(BaseModel):
    """A specification document that the agent MUST read before performing specific tasks."""
    id: Optional[int] = None
    project: str = Field(default="global", description="Project identifier or 'global'")
    trigger_pattern: str = Field(description="Comma-separated keywords or regex that triggers this requirement")
    spec_path: str = Field(description="Path to the specification file (relative to workspace or absolute)")
    instruction: str = Field(default="You must read this spec before planning or generating code.", description="Action directive for the agent")
    created_at: str = Field(default_factory=current_iso_time)


class GoldenPattern(BaseModel):
    """A verified, battle-tested code template or pattern that works 100% of the time."""
    id: Optional[int] = None
    project: str = Field(default="global", description="Project identifier or 'global'")
    context: str = Field(description="Stack/keywords (e.g. 'php, mysql, pdo connection')")
    title: str = Field(description="Short descriptive title of the pattern")
    code_snippet: str = Field(description="The verified working code snippet")
    explanation: str = Field(default="", description="Why this works and what gotchas it prevents")
    created_at: str = Field(default_factory=current_iso_time)


class Experience(BaseModel):
    """An anti-pattern and vaccine learned from a past struggle or error."""
    id: Optional[int] = None
    project: str = Field(default="global", description="Project identifier or 'global'")
    context: str = Field(description="Stack/keywords (e.g. 'php, mysql, utf8mb4')")
    what_failed: str = Field(description="The trap: what the AI did wrong or what caused errors")
    fix_applied: str = Field(description="The vaccine: what actually resolved the problem")
    recurrence_count: int = Field(default=1, description="Times this pattern was encountered/reinforced")
    created_at: str = Field(default_factory=current_iso_time)
    updated_at: str = Field(default_factory=current_iso_time)


class ConsultationResult(BaseModel):
    """The aggregate knowledge returned by MegaBrain for a given prompt/task context."""
    project: str
    context_query: str
    rules: list[Rule] = Field(default_factory=list)
    mandatory_specs: list[MandatorySpec] = Field(default_factory=list)
    golden_patterns: list[GoldenPattern] = Field(default_factory=list)
    experiences: list[Experience] = Field(default_factory=list)
    formatted_prompt: str = Field(description="Markdown guardrail text ready to inject into the agent's context")
