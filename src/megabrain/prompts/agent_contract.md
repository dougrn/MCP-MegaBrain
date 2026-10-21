# 🧠 MegaBrain Agent Behavioral Contract

Add this rule to your agent's system prompt (e.g., in `.agents/rules/megabrain.md`, `.cursorrules`, `.clinerules`, or Claude project instructions):

```markdown
# MegaBrain Protocol (Persistent Knowledge & Autonomous Vaccine)

You are equipped with MegaBrain, an external memory system that tracks rules, mandatory specs, and vaccines against repeated AI errors.

## 1. MANDATORY PRE-FLIGHT CONSULTATION
BEFORE generating code, creating architectures, querying databases, or touching UI design:
- Identify the current project from the workspace folder or git repo (e.g., 'ldg', 'casafleet', 'buscapjota').
- Call `brain_consult(context="<stack/keywords>", project="<project_id>")`.
- **Prerequisite Specs**: If any mandatory specs are returned, you are FORBIDDEN from writing code or plans until you have read the file using your file viewing tool.
- **Golden Patterns**: If a verified snippet is provided, you MUST adopt it instead of inventing your own implementation.
- **AI Blind Spots / Traps**: Carefully avoid the listed anti-patterns and apply the proven fixes.

## 2. MANDATORY PRE-COMPLETION VACCINE (AUTONOMOUS GATEKEEPER)
BEFORE concluding any turn or delivering your final answer to the user, you MUST review your execution:
- Did any command, script, build, or test fail with exit code != 0, Traceback, TypeError, PDOException, SyntaxError, or runtime error during your execution?
- Did you have to fix code, change parameters, or debug an unexpected behavior?
👉 IF YES: You are STRICTLY FORBIDDEN from ending your turn without FIRST calling:
`brain_record_experience(context="<stack/domain>", what_failed="<exact_error>", fix_applied="<working_solution>", project="<project_or_global>")`
- **Scope Rule**:
  - For language/runtime bugs (Python, PHP, React, Docker, SQL, cURL), use `project="global"` so all projects benefit.
  - For project-specific business rules or architecture, use `project="<current_project>"`.
- If a clean reusable snippet was the fix, pass `verified_snippet`.
DO NOT wait for the user to ask. Recording vaccines after resolving errors is an AUTONOMOUS SYSTEM DUTY.

## 3. USER TRIGGER PHRASES & RULES
- "Grava isso no cérebro" / "Aprende isso" / "Vacina contra esse erro" / "Remember this":
  - Immediately extract: context keywords, what failed, and exact working solution.
  - Call `brain_record_experience(..., project="<project_or_global>")`.
- "Salva como regra" / "Registre essa regra" / "Não faça mais isso, é regra":
  - Extract the constraint statement and category.
  - Call `brain_record_rule(rule="...", category="...", project="<current_project>")`.
  - CRITICAL: ALWAYS scope project-specific rules to the current project. NEVER mark project architecture, UI, or business logic as 'global'.
```
