# 🧠 MegaBrain Agent Behavioral Contract

Add this rule to your agent's system prompt (e.g., in `.agents/rules/megabrain.md`, `.cursorrules`, `.clinerules`, or Claude project instructions):

```markdown
# MegaBrain Protocol (Persistent Knowledge & Vaccine)

You have access to MegaBrain via MCP tools. You MUST strictly adhere to this execution protocol:

## 1. Mandatory Pre-Flight Consultation
BEFORE generating code, creating architectures, querying databases, or touching UI design:
- Call `brain_consult(context="<stack/keywords>", project="<project_id_or_global>")`.
- **Prerequisite Specs**: If any mandatory specs are returned, you are FORBIDDEN from writing code or plans until you have read the file using your file viewing tool.
- **Golden Patterns**: If a verified snippet is provided, you MUST adopt it instead of inventing your own implementation.
- **AI Blind Spots / Traps**: Carefully avoid the listed anti-patterns and apply the proven fixes.

## 2. Autonomous Post-Mortem & Vaccination
- If a task required 2 or more attempts to succeed (e.g. debugging terminal errors, syntax issues, runtime warnings), OR
- If you discovered an undocumented quirk or breaking change:
  - IMMEDIATELY call `brain_record_experience(context="...", what_failed="...", fix_applied="...", project="...")`.
  - If a clean, reusable code snippet solved the issue, pass it to `verified_snippet`.

## 3. Human Triggers
If the user says "Grava isso no cérebro", "Aprende isso", "Vacina contra esse erro", or "Remember this":
- Immediately analyze the recent context.
- Extract: the context keywords, the rookie mistake/trap, and the exact working solution.
- Call `brain_record_experience`.
```
