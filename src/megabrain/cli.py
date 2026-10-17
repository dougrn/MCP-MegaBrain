"""Rich Command Line Interface (CLI) for MegaBrain."""

import argparse
import sys
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from megabrain.db import MegaBrainDB
from megabrain.server import server

console = Console()
db = MegaBrainDB()

AGENT_CONTRACT_TEXT = """
# 🧠 MEGABRAIN AGENT CONTRACT (VACCINATION & AUTONOMOUS LEARNING)

You are equipped with MegaBrain (a persistent memory and anti-pattern vaccine).
To guarantee consistent code quality and prevent repeating known mistakes, you MUST follow these mandatory protocols:

### 1. MANDATORY PRE-FLIGHT CHECK (BEFORE GENERATING CODE)
Before writing code, designing architecture, querying databases, or refactoring:
- Call `brain_consult(context="...", project="...")`.
- If **Prerequisite Specifications** are returned: You MUST inspect/read the specified files BEFORE generating code or plans.
- If **Golden Patterns** are returned: You are FORBIDDEN from reinventing your own boilerplate; you MUST adopt the verified snippet.
- If **Known AI Blind Spots** are returned: Pay extreme attention to the anti-patterns and use the proven fix.

### 2. AUTONOMOUS SELF-IMPROVEMENT (AFTER RESOLVING ERRORS)
Whenever you:
- Spend 2 or more attempts trying to fix an error, OR
- Encounter an unexpected runtime error (e.g. SQL syntax, deprecation warning, framework quirk), OR
- Discover a non-obvious requirement or fix:
**Immediately call `brain_record_experience(context="...", what_failed="...", fix_applied="...", project="...")`** so this lesson is vaccinated permanently across all sessions.

### 3. USER TRIGGER PHRASES
If the user says:
- *"Grava isso no cérebro"* / *"Aprende isso"* / *"Remember this"* / *"Vaccine against this"*:
Immediately extract the root cause, what failed, and what worked, then call `brain_record_experience`.
"""


def cmd_consult(args):
    """Consult MegaBrain for a given context and project."""
    res = db.consult(context_query=args.context, project=args.project)
    if args.raw:
        print(res.formatted_prompt)
    else:
        console.print(Markdown(res.formatted_prompt))


def cmd_record_rule(args):
    """Add a new rule."""
    rule = db.add_rule(
        rule=args.rule,
        category=args.category,
        project=args.project,
        severity=args.severity,
    )
    console.print(
        f"[bold green]✔ Rule added[/bold green] [dim]#{rule.id}[/dim] for "
        f"[cyan]{rule.project}[/cyan] ({rule.category}): [yellow][{rule.severity}][/yellow] {rule.rule}"
    )


def cmd_record_spec(args):
    """Register a prerequisite spec."""
    spec = db.add_spec(
        spec_path=args.spec_path,
        trigger_pattern=args.trigger,
        instruction=args.instruction or "",
        project=args.project,
    )
    console.print(
        f"[bold green]✔ Prerequisite Spec added[/bold green] [dim]#{spec.id}[/dim] for "
        f"[cyan]{spec.project}[/cyan]: Trigger [yellow]'{spec.trigger_pattern}'[/yellow] -> [bold]{spec.spec_path}[/bold]"
    )


def cmd_record_experience(args):
    """Record an anti-pattern and vaccine."""
    exp = db.record_experience(
        context=args.context,
        what_failed=args.failed,
        fix_applied=args.fix,
        project=args.project,
    )
    console.print(
        f"[bold green]✔ Experience vaccinated[/bold green] [dim]#{exp.id}[/dim] (Recurrence: {exp.recurrence_count}x)\n"
        f"  [red]Trap:[/red] {exp.what_failed}\n"
        f"  [green]Fix:[/green] {exp.fix_applied}"
    )


def cmd_golden_pattern(args):
    """Record a golden pattern."""
    pat = db.add_golden_pattern(
        title=args.title,
        context=args.context,
        code_snippet=args.code,
        explanation=args.explanation or "",
        project=args.project,
    )
    console.print(f"[bold green]✔ Golden Pattern saved[/bold green] [dim]#{pat.id}[/dim]: '{pat.title}'")


def cmd_stats(args):
    """Show database stats."""
    stats = db.get_stats()
    table = Table(title="🧠 MegaBrain Memory Statistics", header_style="bold magenta")
    table.add_column("Category", style="cyan")
    table.add_column("Count", justify="right", style="green")

    table.add_row("Rules & Hard Constraints", str(stats["rules"]))
    table.add_row("Prerequisite Specifications", str(stats["mandatory_specs"]))
    table.add_row("Vaccinated Experiences (Anti-Patterns)", str(stats["experiences"]))
    table.add_row("Golden Patterns (Verified Snippets)", str(stats["golden_patterns"]))

    console.print(table)
    console.print(f"[dim]Database path: {stats['db_path']}[/dim]")


def cmd_list(args):
    """List stored items."""
    target = args.type.lower()
    project = args.project

    if target in ("rules", "rule", "r"):
        rules = db.list_rules(project)
        table = Table(title=f"Rules (Project: {project})", header_style="bold cyan")
        table.add_column("ID", style="dim", width=4)
        table.add_column("Project", style="cyan")
        table.add_column("Severity", style="yellow")
        table.add_column("Category", style="blue")
        table.add_column("Rule", style="white")
        for r in rules:
            table.add_row(str(r.id), r.project, r.severity, r.category, r.rule)
        console.print(table)

    elif target in ("specs", "spec", "s"):
        specs = db.list_specs(project)
        table = Table(title=f"Prerequisite Specs (Project: {project})", header_style="bold cyan")
        table.add_column("ID", style="dim", width=4)
        table.add_column("Project", style="cyan")
        table.add_column("Trigger Pattern", style="yellow")
        table.add_column("File Path", style="green")
        table.add_column("Instruction", style="white")
        for s in specs:
            table.add_row(str(s.id), s.project, s.trigger_pattern, s.spec_path, s.instruction)
        console.print(table)

    elif target in ("experiences", "exp", "e", "traps"):
        experiences = db.list_experiences(project)
        table = Table(title=f"Vaccinated Experiences / Traps (Project: {project})", header_style="bold cyan")
        table.add_column("ID", style="dim", width=4)
        table.add_column("Project", style="cyan")
        table.add_column("Context", style="yellow")
        table.add_column("Recurrence", justify="center", style="magenta")
        table.add_column("What Failed (Trap)", style="red")
        table.add_column("Fix Applied (Vaccine)", style="green")
        for e in experiences:
            table.add_row(str(e.id), e.project, e.context, f"{e.recurrence_count}x", e.what_failed, e.fix_applied)
        console.print(table)

    elif target in ("patterns", "pat", "p", "golden"):
        patterns = db.list_golden_patterns(project)
        table = Table(title=f"Golden Patterns (Project: {project})", header_style="bold cyan")
        table.add_column("ID", style="dim", width=4)
        table.add_column("Project", style="cyan")
        table.add_column("Title", style="green")
        table.add_column("Context", style="yellow")
        table.add_column("Snippet Preview", style="dim")
        for p in patterns:
            snippet_preview = p.code_snippet[:40].replace("\n", " ") + "..."
            table.add_row(str(p.id), p.project, p.title, p.context, snippet_preview)
        console.print(table)
    else:
        console.print(f"[red]Unknown list type: {target}. Use 'rules', 'specs', 'experiences', or 'patterns'.[/red]")


def cmd_contract(args):
    """Print the Agent Contract text for easy copy-pasting."""
    if args.raw:
        print(AGENT_CONTRACT_TEXT.strip())
    else:
        console.print(Panel(Markdown(AGENT_CONTRACT_TEXT.strip()), title="MegaBrain Agent Contract", border_style="cyan"))


def cmd_serve(args):
    """Run the MCP server."""
    console.print("[bold green]Starting MegaBrain MCP Server (stdio)...[/bold green]")
    server.run(transport="stdio")


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        prog="megabrain",
        description="🧠 MegaBrain: Persistent cross-agent memory, rule enforcer, and blindspot vaccine.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # consult
    p_consult = subparsers.add_parser("consult", help="Consult active rules, specs, and anti-patterns")
    p_consult.add_argument("context", help="Task context or technology keywords (e.g. 'php mysql', 'login component')")
    p_consult.add_argument("--project", "-p", default="global", help="Project name or 'global'")
    p_consult.add_argument("--raw", action="store_true", help="Print raw unstyled markdown (useful for piping into llama.cpp)")
    p_consult.set_defaults(func=cmd_consult)

    # record-rule
    p_rule = subparsers.add_parser("record-rule", help="Record a hard rule or constraint")
    p_rule.add_argument("rule", help="Rule statement (e.g. 'All comments must be in English')")
    p_rule.add_argument("--category", "-c", default="general", help="Category: language, architecture, security, git, etc.")
    p_rule.add_argument("--project", "-p", default="global", help="Project name or 'global'")
    p_rule.add_argument("--severity", "-s", default="CRITICAL", choices=["CRITICAL", "HIGH", "MEDIUM", "LOW"])
    p_rule.set_defaults(func=cmd_record_rule)

    # record-spec
    p_spec = subparsers.add_parser("record-spec", help="Register a prerequisite spec that must be read")
    p_spec.add_argument("spec_path", help="Path to specification file (e.g. 'specs/design.md')")
    p_spec.add_argument("--trigger", "-t", required=True, help="Comma-separated trigger keywords (e.g. 'design,ui,layout')")
    p_spec.add_argument("--instruction", "-i", default="", help="Directive for the agent")
    p_spec.add_argument("--project", "-p", default="global", help="Project name or 'global'")
    p_spec.set_defaults(func=cmd_record_spec)

    # record-experience
    p_exp = subparsers.add_parser("record-experience", help="Record an error trap and its working fix")
    p_exp.add_argument("--context", "-c", required=True, help="Stack/domain keywords (e.g. 'php mysql')")
    p_exp.add_argument("--failed", "-f", required=True, help="What the AI did wrong / trap encountered")
    p_exp.add_argument("--fix", "-x", required=True, help="The working solution / vaccine")
    p_exp.add_argument("--project", "-p", default="global", help="Project name or 'global'")
    p_exp.set_defaults(func=cmd_record_experience)

    # golden-pattern
    p_pat = subparsers.add_parser("golden-pattern", help="Save a verified working code snippet")
    p_pat.add_argument("--title", "-t", required=True, help="Title of the pattern")
    p_pat.add_argument("--context", "-c", required=True, help="Stack/domain keywords (e.g. 'php mysql pdo')")
    p_pat.add_argument("--code", required=True, help="Verified working code snippet")
    p_pat.add_argument("--explanation", "-e", default="", help="Explanation of why this snippet is required")
    p_pat.add_argument("--project", "-p", default="global", help="Project name or 'global'")
    p_pat.set_defaults(func=cmd_golden_pattern)

    # stats
    p_stats = subparsers.add_parser("stats", help="Show knowledge base statistics")
    p_stats.set_defaults(func=cmd_stats)

    # list
    p_list = subparsers.add_parser("list", help="List stored items")
    p_list.add_argument("type", choices=["rules", "specs", "experiences", "patterns"], help="Item type to list")
    p_list.add_argument("--project", "-p", default="all", help="Filter by project or 'all'")
    p_list.set_defaults(func=cmd_list)

    # contract
    p_contract = subparsers.add_parser("contract", help="Output agent contract prompt instructions")
    p_contract.add_argument("--raw", action="store_true", help="Print raw text without formatting panel")
    p_contract.set_defaults(func=cmd_contract)

    # serve
    p_serve = subparsers.add_parser("serve", help="Run the MCP server (stdio transport)")
    p_serve.set_defaults(func=cmd_serve)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
