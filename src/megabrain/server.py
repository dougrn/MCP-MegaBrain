"""Model Context Protocol (MCP) Server for MegaBrain."""

from typing import Optional
from megabrain.db import MegaBrainDB

# Compatibility import for mcp 1.x and 2.x
try:
    from mcp.server.mcpserver import MCPServer
except ImportError:
    from mcp.server.fastmcp import FastMCP as MCPServer

# Initialize server and database
server = MCPServer(
    name="MegaBrain",
    instructions=(
        "MegaBrain is your persistent external brain and memory across all AI coding sessions. "
        "Before generating code, querying databases, or designing features, you MUST call `brain_consult`. "
        "After solving a tricky bug, struggling with retries, or discovering a non-obvious pitfall, "
        "you MUST call `brain_record_experience` so the mistake is vaccinated and never repeated."
    ),
)
db = MegaBrainDB()


@server.tool()
def brain_consult(context: str = "", project: str = "global") -> str:
    """
    MANDATORY PRE-FLIGHT CHECK: Call this before writing, designing, or refactoring code.
    Returns:
    - Active project rules & hard constraints
    - Prerequisite specifications you MUST inspect before coding
    - Known AI blind spots (previous traps & working vaccines)
    - Golden Patterns (verified working code snippets to use directly)

    Args:
        context: The topic, stack, or task description (e.g., 'php mysql pdo', 'react button design', 'authentication'). Leave empty or 'all' to load everything.
        project: Project name/slug or 'global'
    """
    result = db.consult(context_query=context, project=project)
    return result.formatted_prompt


@server.tool()
def brain_load_project(project: str = "global") -> str:
    """
    LOAD COMPLETE BRAIN KNOWLEDGE: Call this whenever the user says:
    - 'leia todas as regras do projeto'
    - 'carregue as regras do MegaBrain'
    - 'load all project rules'
    - 'what are the rules for this project?'
    Returns all active rules, mandatory specifications, anti-patterns, and golden patterns for the project.

    Args:
        project: Project identifier (e.g., 'ldg', 'ecommerce', or 'global')
    """
    result = db.consult(context_query="all", project=project)
    return result.formatted_prompt


@server.tool()
def brain_record_experience(
    context: str,
    what_failed: str,
    fix_applied: str,
    project: str = "global",
    verified_snippet: str = "",
) -> str:
    """
    VACCINATE AGAINST MISTAKES: Call this whenever you spent >= 2 attempts fixing an error,
    encountered an unexpected runtime pitfall, or when the user says 'grava isso' / 'aprende isso'.

    Args:
        context: Stack/domain keywords (e.g., 'php mysql utf8mb4', 'docker windows networking')
        what_failed: The anti-pattern or rookie mistake the AI made
        fix_applied: The exact working solution or insight that solved it
        project: Project identifier or 'global'
        verified_snippet: (Optional) The working code block to also save as a Golden Pattern
    """
    exp = db.record_experience(
        context=context,
        what_failed=what_failed,
        fix_applied=fix_applied,
        project=project,
    )

    pattern_msg = ""
    if verified_snippet and verified_snippet.strip():
        title = f"Fix for: {what_failed[:50]}"
        pat = db.add_golden_pattern(
            title=title,
            context=context,
            code_snippet=verified_snippet.strip(),
            explanation=fix_applied,
            project=project,
        )
        pattern_msg = f" Also created Golden Pattern #{pat.id} ('{pat.title}')."

    return (
        f"✅ Experience recorded successfully [ID: {exp.id}, Recurrence: {exp.recurrence_count}x]. "
        f"Trap '{what_failed[:40]}...' is now vaccinated for '{context}'.{pattern_msg}"
    )


@server.tool()
def brain_record_rule(
    rule: str,
    category: str = "general",
    project: str = "global",
    severity: str = "CRITICAL",
) -> str:
    """
    Enforce a strict constraint that agents must always obey.

    Args:
        rule: The constraint statement (e.g., 'All code comments and docs must be in English')
        category: Category like 'language', 'architecture', 'security', 'git', 'style', 'general'
        project: Project identifier or 'global'
        severity: 'CRITICAL', 'HIGH', 'MEDIUM', or 'LOW'
    """
    created = db.add_rule(rule=rule, category=category, project=project, severity=severity)
    return f"✅ Rule registered [ID: {created.id}] for project '{created.project}': [{created.severity}] {created.rule}"


@server.tool()
def brain_require_spec(
    spec_path: str,
    trigger_pattern: str,
    instruction: str = "",
    project: str = "global",
) -> str:
    """
    Register a specification file that the agent MUST read before working on matching topics.

    Args:
        spec_path: Path to spec file (e.g., 'specs/design-tokens.md', 'docs/api.md')
        trigger_pattern: Comma-separated keywords triggering this requirement (e.g., 'design, ui, layout, componentes')
        instruction: Directive for the agent (e.g., 'Read design tokens before generating CSS')
        project: Project identifier or 'global'
    """
    spec = db.add_spec(
        spec_path=spec_path,
        trigger_pattern=trigger_pattern,
        instruction=instruction,
        project=project,
    )
    return (
        f"✅ Prerequisite Spec registered [ID: {spec.id}] for project '{spec.project}': "
        f"When task matches '{spec.trigger_pattern}' -> MUST read '{spec.spec_path}'."
    )


@server.tool()
def brain_record_golden_pattern(
    title: str,
    context: str,
    code_snippet: str,
    explanation: str = "",
    project: str = "global",
) -> str:
    """
    Save a battle-tested code snippet that agents must copy/adopt instead of reinventing boilerplate.

    Args:
        title: Short descriptive title
        context: Stack/domain keywords (e.g., 'php mysql pdo')
        code_snippet: The exact verified working code
        explanation: Explanation of why this pattern is preferred
        project: Project identifier or 'global'
    """
    pat = db.add_golden_pattern(
        title=title,
        context=context,
        code_snippet=code_snippet,
        explanation=explanation,
        project=project,
    )
    return f"✅ Golden Pattern registered [ID: {pat.id}]: '{pat.title}' for context '{pat.context}'."


@server.tool()
def brain_list_rules(project: str = "global") -> str:
    """List all active rules for the given project including global rules."""
    rules = db.list_rules(project=project)
    if not rules:
        return f"No rules recorded for project '{project}'."
    lines = [f"### Rules for project '{project}':"]
    for r in rules:
        lines.append(f"- [{r.id}] **[{r.severity}] ({r.project} / {r.category})**: {r.rule}")
    return "\n".join(lines)


@server.tool()
def brain_stats() -> str:
    """Get current knowledge base statistics."""
    stats = db.get_stats()
    return (
        f"📊 MegaBrain Database: {stats['db_path']}\n"
        f"- Rules: {stats['rules']}\n"
        f"- Mandatory Specs: {stats['mandatory_specs']}\n"
        f"- Experiences (Vaccines): {stats['experiences']}\n"
        f"- Golden Patterns: {stats['golden_patterns']}"
    )


# MCP Resources
@server.resource("megabrain://rules")
def resource_rules() -> str:
    """Read all global and project rules."""
    rules = db.list_rules("all")
    return "\n".join([f"- [{r.project} / {r.severity}] ({r.category}): {r.rule}" for r in rules])


@server.resource("megabrain://stats")
def resource_stats() -> str:
    """Read knowledge base statistics."""
    return brain_stats()


def main():
    """Main entrypoint for MCP stdio transport."""
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
