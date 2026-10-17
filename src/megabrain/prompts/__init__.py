"""Prompts and agent rule templates for MegaBrain."""
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent


def get_agent_contract() -> str:
    """Read the standard Agent Contract markdown file."""
    contract_file = PROMPTS_DIR / "agent_contract.md"
    return contract_file.read_text(encoding="utf-8")
