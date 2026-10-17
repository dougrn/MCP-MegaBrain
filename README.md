# 🧠 MegaBrain (MCP)

> **Persistent Cross-Agent Memory, Rule Enforcer, and Blindspot Vaccine for AI Coding Assistants.**  
> Compatible with **Claude Desktop**, **VS Code (Cline, Roo Code, Continue)**, **Antigravity IDE**, and **Local AI (llama.cpp)**.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-purple.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![uv](https://img.shields.io/badge/managed%20by-uv-orange.svg)](https://github.com/astral-sh/uv)
[![Tests](https://img.shields.io/badge/tests-13%20passed-brightgreen.svg)]()

---

## 🎯 The Problem

When vibecoding with AI coding agents (Claude, Antigravity, or local LLMs via `llama.cpp`), developers face two relentless frustrations:

1. **Relentless Repetitive Errors (AI Blind Spots)**:  
   The AI writes a PHP/MySQL script and fails on the first try *every single time*, blindly retrying until it works. In the next session, it resets its memory and makes the exact same mistake again.
2. **Context & Spec Amnesia**:  
   The AI ignores project rules (e.g., answering in Portuguese when English is strictly required) or writes UI components without reading the project's design specifications.

---

## 💡 The Solution: MegaBrain

**MegaBrain** is an autonomous memory engine running locally via the **Model Context Protocol (MCP)**. It stores rules, mandatory specifications, and battle-tested code snippets in a high-speed SQLite database with **FTS5 full-text search**.

Because MegaBrain uses a single local database (`~/.megabrain/megabrain.db`), **any lesson learned by Claude or Antigravity is instantly available to your local llama.cpp model in VS Code, and vice-versa**.

```
                ┌───────────────────────────────────┐
                │        MegaBrain SQLite DB        │
                │     (~/.megabrain/megabrain.db)   │
                └─────────────────┬─────────────────┘
                                  │ (MCP / CLI)
         ┌────────────────────────┼────────────────────────┐
         │                        │                        │
         ▼                        ▼                        ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Claude Desktop  │    │  VS Code (Cline) │    │ Antigravity IDE  │
│  & Claude Code   │    │  & llama.cpp     │    │                  │
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

---

## ⚡ The 3 Pillars

### 1. Mandatory Pre-Flight Check (`brain_consult`)
Before the AI generates code, designs layout, or queries databases, it queries MegaBrain with its task context. MegaBrain immediately surfaces:
* **Strict Constraints**: E.g., `STRICT_LANGUAGE: English`.
* **Prerequisite Specs**: Traps the agent: *"You are FORBIDDEN from generating layout code before reading `specs/design-tokens.md`"*.
* **Known Blind Spots**: E.g., *"You repeatedly fail PDO connection syntax. Do NOT use X; use Y."*
* **Golden Patterns**: Verified, working code snippets.

### 2. Autonomous Post-Mortem Vaccine (`brain_record_experience`)
Whenever the agent takes $\ge 2$ attempts to fix an error, or when the user says *"Grava isso no cérebro"* (*"Remember this"*), the agent records what failed and what worked.  
MegaBrain tracks a **recurrence counter** and vaccinates the entire environment against that mistake.

### 3. Golden Patterns (Verified Code Snippets)
Instead of letting the AI hallucinate boilerplates from average internet tokens, MegaBrain stores validated implementations that the AI must adopt directly.

---

## 🚀 Quickstart

### Prerequisites
* Python 3.10 or higher
* [uv](https://docs.astral.sh/uv/) (recommended) or standard `pip`

### Installation

```powershell
# 1. Clone the repository
git clone https://github.com/your-username/MCP-MegaBrain.git
cd MCP-MegaBrain

# 2. Sync dependencies with uv
uv sync
```

### Try the CLI

```powershell
# View knowledge base stats
uv run megabrain stats

# Add a strict rule
uv run megabrain record-rule "All code comments and docs must be in English" --category language --project my-app

# Require a spec before touching design
uv run megabrain record-spec "specs/design-tokens.md" --trigger "design,ui,layout" --project my-app

# Record an anti-pattern vaccine
uv run megabrain record-experience --context "php mysql" --failed "Called set_charset on uninitialized PDO" --fix "Pass charset=utf8mb4 inside DSN string"

# Save a verified Golden Pattern
uv run megabrain golden-pattern --title "PHP PDO UTF8MB4" --context "php mysql pdo" --code "$pdo = new PDO('mysql:host=localhost;dbname=test;charset=utf8mb4', $user, $pass, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);"

# Consult MegaBrain (see what the AI receives!)
uv run megabrain consult "php mysql query" --project my-app
```

---

## 🔌 Connecting to Your AI Clients

### 1. Claude Desktop
Add to your `claude_desktop_config.json`:
* **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
* **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "megabrain": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "C:\\Users\\dougl\\Desktop\\Serviços\\_Pessoais\\MCP-MegaBrain",
        "megabrain-server"
      ]
    }
  }
}
```

### 2. VS Code (Cline / Roo Code)
Add to your Cline MCP settings:

```json
{
  "mcpServers": {
    "megabrain": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "C:\\Users\\dougl\\Desktop\\Serviços\\_Pessoais\\MCP-MegaBrain",
        "megabrain-server"
      ],
      "disabled": false,
      "autoApprove": [
        "brain_consult",
        "brain_record_experience",
        "brain_stats"
      ]
    }
  }
}
```

### 3. Antigravity IDE
Add to your MCP server configuration:

```json
{
  "mcpServers": {
    "megabrain": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "C:\\Users\\dougl\\Desktop\\Serviços\\_Pessoais\\MCP-MegaBrain",
        "megabrain-server"
      ]
    }
  }
}
```

### 4. Local AI (llama.cpp)
Run the prompt enricher before passing prompts to `llama-server` or CLI:

```powershell
uv run python examples/llama-cpp-wrapper/query_megabrain.py
```

---

## 📜 The Agent Behavioral Contract

To guarantee that your AI assistant actively consults MegaBrain and records mistakes autonomously, add the following prompt rule to your agent's instructions (e.g. `.cursorrules`, `.agents/rules/megabrain.md`, or Claude project instructions):

```markdown
# MegaBrain Protocol (Persistent Knowledge & Vaccine)

You are equipped with MegaBrain via MCP tools. You MUST follow these mandatory protocols:

## 1. MANDATORY PRE-FLIGHT CONSULTATION
BEFORE generating code, proposing architecture, querying databases, or touching UI design:
- Call `brain_consult(context="<stack/keywords>", project="<project_id_or_global>")`.
- **Prerequisite Specs**: If any mandatory specs are returned, you are strictly FORBIDDEN from writing code or plans until you inspect the spec file using your file reading tool.
- **Golden Patterns**: If a verified snippet is provided, you MUST adopt it instead of inventing your own implementation.
- **AI Blind Spots / Traps**: Carefully avoid the listed anti-patterns and apply the proven fixes.

## 2. AUTONOMOUS SELF-IMPROVEMENT (POST-MORTEM VACCINE)
Whenever you:
- Spend 2 or more attempts trying to fix an error in a terminal/script, OR
- Discover a non-obvious bug or runtime pitfall:
  - IMMEDIATELY call `brain_record_experience(context="...", what_failed="...", fix_applied="...", project="...")`.
  - If a clean, reusable code snippet solved the issue, pass it to `verified_snippet`.

## 3. HUMAN TRIGGERS
If the user says:
- "Grava isso no cérebro" / "Aprende isso" / "Vacina contra esse erro" / "Remember this":
  - Immediately extract the context keywords, what failed, and the working fix.
  - Call `brain_record_experience`.
```

---

## 🛠️ CLI Reference

| Command | Description | Example |
| :--- | :--- | :--- |
| `megabrain consult` | Query active rules, specs, and vaccines | `megabrain consult "php mysql" -p myapp` |
| `megabrain record-rule` | Enforce a strict constraint | `megabrain record-rule "Only English" -c language` |
| `megabrain record-spec` | Bind a spec file to topic triggers | `megabrain record-spec "specs/api.md" -t "api,rest"` |
| `megabrain record-experience`| Vaccinate against a repeated error | `megabrain record-experience -c "pdo" -f "..." -x "..."` |
| `megabrain golden-pattern` | Save a battle-tested code snippet | `megabrain golden-pattern -t "Title" -c "tag" --code "..."` |
| `megabrain list` | List stored memory by type | `megabrain list rules` / `megabrain list experiences` |
| `megabrain stats` | Display memory overview & item counts | `megabrain stats` |
| `megabrain contract` | Output the agent system instructions | `megabrain contract --raw` |
| `megabrain serve` | Launch MCP server over stdio | `megabrain serve` |

---

## 🧪 Running Tests

```powershell
uv run pytest
```
All 13 test suites validate schema migrations, FTS5 full-text search, recurrence increments, and MCP tool executions.

---

## 🇧🇷 Resumo em Português

O **MCP-MegaBrain** é um cérebro persistente para desenvolvedores que trabalham com múltiplos agentes (Antigravity, Claude, VS Code/Cline, llama.cpp). Ele resolve de forma definitiva:
* **Erros repetitivos e teimosia da IA**: Transforma bugs corrigidos em "vacinas" com contador de recorrência.
* **Amnésia de especificações**: Obriga a IA a ler suas specs de design/arquitetura antes de emitir código.
* **Desobediência de regras**: Garante conformidade com idioma, padrões de commit e restrições de arquitetura.
* **100% Local e Gratuito**: Armazenado em SQLite local com busca instantânea (FTS5), sem mensalidades ou nuvem.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
