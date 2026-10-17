# 🧠 MegaBrain Universal Agent Rule

Copy and paste this rule into your agent system instructions:
- Antigravity IDE: `.agents/rules/megabrain.md`
- Cursor: `.cursorrules`
- VS Code Cline / Roo Code: Custom Instructions in Settings
- Claude Desktop: Project Custom Instructions

---

```markdown
# MegaBrain Protocol (Persistent Knowledge & Vaccine)

You are equipped with MegaBrain, an external memory system that tracks rules, mandatory specs, and vaccines against repeated AI errors.

## 1. MANDATORY PRE-FLIGHT CONSULTATION
BEFORE generating code, proposing architecture, querying databases, or touching UI design:
- Call the MCP tool `brain_consult(context="<stack/keywords>", project="<project_id_or_global>")`.
- **Prerequisite Specs**: If any mandatory specs are returned, you are strictly FORBIDDEN from writing code or plans until you inspect the spec file using your file reading tool.
- **Golden Patterns**: If a verified snippet is provided, you MUST adopt it instead of inventing your own implementation.
- **AI Blind Spots / Traps**: Carefully avoid the listed anti-patterns and apply the proven fixes.

## 2. AUTONOMOUS SELF-IMPROVEMENT (POST-MORTEM VACCINE)
Whenever you:
- Spend 2 or more attempts trying to fix an error in a terminal/script, OR
- Discover a non-obvious bug or runtime pitfall:
  - IMMEDIATELY call `brain_record_experience(context="...", what_failed="...", fix_applied="...", project="...")`.
  - If a clean, reusable code snippet solved the issue, pass it to `verified_snippet`.

## 3. USER TRIGGER PHRASES
If the user says:
- "Grava isso no cérebro" / "Aprende isso" / "Vacina contra esse erro" / "Remember this":
  - Immediately extract the context keywords, what failed, and the working fix.
  - Call `brain_record_experience`.
```
