"""Example: Inject MegaBrain guardrails into local llama.cpp prompts."""

import sys
from megabrain.db import MegaBrainDB

def enrich_prompt_for_llama(user_prompt: str, context_tags: str, project: str = "global") -> str:
    """
    Fetch active rules, mandatory specs, and anti-pattern vaccines from MegaBrain,
    and prepend them to the system prompt or user prompt for llama.cpp.
    """
    db = MegaBrainDB()
    consultation = db.consult(context_query=context_tags, project=project)

    full_prompt = (
        f"{consultation.formatted_prompt}\n"
        f"---\n"
        f"USER REQUEST:\n{user_prompt}\n"
    )
    return full_prompt


if __name__ == "__main__":
    test_prompt = "Write a PHP script to query users from MySQL"
    tags = "php mysql pdo"
    enriched = enrich_prompt_for_llama(test_prompt, tags)
    print("=== ENRICHED PROMPT READY FOR LLAMA.CPP ===")
    print(enriched)
