"""SQLite database manager with FTS5 search for MegaBrain."""

import re
import sqlite3
from pathlib import Path
from typing import Optional, Union

from megabrain.config import get_db_path
from megabrain.models import (
    ConsultationResult,
    Experience,
    GoldenPattern,
    MandatorySpec,
    Rule,
    current_iso_time,
)


class MegaBrainDB:
    """Encapsulates all SQLite storage, FTS5 indexing, and consultation logic."""

    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        if db_path == ":memory:" or (isinstance(db_path, Path) and str(db_path) == ":memory:"):
            self.db_path = Path(":memory:")
            self._is_memory = True
            self._mem_conn = sqlite3.connect(":memory:")
            self._mem_conn.row_factory = sqlite3.Row
            self._mem_conn.execute("PRAGMA foreign_keys=ON;")
        else:
            self.db_path = Path(db_path) if db_path else get_db_path()
            self._is_memory = False
            self._mem_conn = None
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Create and configure a SQLite connection."""
        if self._is_memory and self._mem_conn is not None:
            return self._mem_conn
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _init_db(self) -> None:
        """Create tables and FTS5 indexes if they do not exist."""
        with self.get_connection() as conn:
            # 1. Rules table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project TEXT NOT NULL DEFAULT 'global',
                    category TEXT NOT NULL DEFAULT 'general',
                    rule TEXT NOT NULL,
                    severity TEXT NOT NULL DEFAULT 'CRITICAL',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_rules_project ON rules(project);")

            # 2. Mandatory specs table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS mandatory_specs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project TEXT NOT NULL DEFAULT 'global',
                    trigger_pattern TEXT NOT NULL,
                    spec_path TEXT NOT NULL,
                    instruction TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_specs_project ON mandatory_specs(project);")

            # 3. Golden patterns table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS golden_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project TEXT NOT NULL DEFAULT 'global',
                    context TEXT NOT NULL,
                    title TEXT NOT NULL,
                    code_snippet TEXT NOT NULL,
                    explanation TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_patterns_project ON golden_patterns(project);")

            # FTS5 for golden patterns
            conn.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS golden_patterns_fts USING fts5(
                    context,
                    title,
                    explanation,
                    content='golden_patterns',
                    content_rowid='id'
                );
                """
            )

            # Triggers for golden_patterns_fts sync
            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS golden_patterns_ai AFTER INSERT ON golden_patterns BEGIN
                    INSERT INTO golden_patterns_fts(rowid, context, title, explanation)
                    VALUES (new.id, new.context, new.title, new.explanation);
                END;
                """
            )
            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS golden_patterns_ad AFTER DELETE ON golden_patterns BEGIN
                    INSERT INTO golden_patterns_fts(golden_patterns_fts, rowid, context, title, explanation)
                    VALUES ('delete', old.id, old.context, old.title, old.explanation);
                END;
                """
            )
            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS golden_patterns_au AFTER UPDATE ON golden_patterns BEGIN
                    INSERT INTO golden_patterns_fts(golden_patterns_fts, rowid, context, title, explanation)
                    VALUES ('delete', old.id, old.context, old.title, old.explanation);
                    INSERT INTO golden_patterns_fts(rowid, context, title, explanation)
                    VALUES (new.id, new.context, new.title, new.explanation);
                END;
                """
            )

            # 4. Experiences (traps & fixes)
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS experiences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project TEXT NOT NULL DEFAULT 'global',
                    context TEXT NOT NULL,
                    what_failed TEXT NOT NULL,
                    fix_applied TEXT NOT NULL,
                    recurrence_count INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_experiences_project ON experiences(project);")

            # FTS5 for experiences
            conn.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS experiences_fts USING fts5(
                    context,
                    what_failed,
                    fix_applied,
                    content='experiences',
                    content_rowid='id'
                );
                """
            )

            # Triggers for experiences_fts sync
            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS experiences_ai AFTER INSERT ON experiences BEGIN
                    INSERT INTO experiences_fts(rowid, context, what_failed, fix_applied)
                    VALUES (new.id, new.context, new.what_failed, new.fix_applied);
                END;
                """
            )
            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS experiences_ad AFTER DELETE ON experiences BEGIN
                    INSERT INTO experiences_fts(experiences_fts, rowid, context, what_failed, fix_applied)
                    VALUES ('delete', old.id, old.context, old.what_failed, old.fix_applied);
                END;
                """
            )
            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS experiences_au AFTER UPDATE ON experiences BEGIN
                    INSERT INTO experiences_fts(experiences_fts, rowid, context, what_failed, fix_applied)
                    VALUES ('delete', old.id, old.context, old.what_failed, old.fix_applied);
                    INSERT INTO experiences_fts(rowid, context, what_failed, fix_applied)
                    VALUES (new.id, new.context, new.what_failed, new.fix_applied);
                END;
                """
            )

    # ==========================
    # Rules CRUD
    # ==========================

    def add_rule(self, rule: str, category: str = "general", project: str = "global", severity: str = "CRITICAL") -> Rule:
        """Add a new rule or constraint."""
        now = current_iso_time()
        project = project.strip().lower() if project else "global"
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO rules (project, category, rule, severity, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (project, category.strip().lower(), rule.strip(), severity.upper(), now, now),
            )
            return Rule(
                id=cursor.lastrowid,
                project=project,
                category=category.strip().lower(),
                rule=rule.strip(),
                severity=severity.upper(),
                created_at=now,
                updated_at=now,
            )

    def list_rules(self, project: Optional[str] = None) -> list[Rule]:
        """List rules, optionally filtered by project or including global."""
        with self.get_connection() as conn:
            if project and project != "all":
                p = project.strip().lower()
                rows = conn.execute(
                    """
                    SELECT * FROM rules 
                    WHERE project = ? OR project = 'global'
                    ORDER BY 
                        CASE severity 
                            WHEN 'CRITICAL' THEN 1 
                            WHEN 'HIGH' THEN 2 
                            WHEN 'MEDIUM' THEN 3 
                            ELSE 4 
                        END, id ASC
                    """,
                    (p,),
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM rules ORDER BY id ASC").fetchall()
            return [Rule(**dict(row)) for row in rows]

    def delete_rule(self, rule_id: int) -> bool:
        """Delete a rule by ID."""
        with self.get_connection() as conn:
            cursor = conn.execute("DELETE FROM rules WHERE id = ?", (rule_id,))
            return cursor.rowcount > 0

    # ==========================
    # Mandatory Specs CRUD
    # ==========================

    def add_spec(self, spec_path: str, trigger_pattern: str, instruction: str = "", project: str = "global") -> MandatorySpec:
        """Register a specification that must be read before performing tasks matching trigger_pattern."""
        now = current_iso_time()
        project = project.strip().lower() if project else "global"
        instruction = instruction.strip() or f"You must read {spec_path} before generating code or plans."
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO mandatory_specs (project, trigger_pattern, spec_path, instruction, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (project, trigger_pattern.strip().lower(), spec_path.strip(), instruction, now),
            )
            return MandatorySpec(
                id=cursor.lastrowid,
                project=project,
                trigger_pattern=trigger_pattern.strip().lower(),
                spec_path=spec_path.strip(),
                instruction=instruction,
                created_at=now,
            )

    def list_specs(self, project: Optional[str] = None) -> list[MandatorySpec]:
        """List mandatory specs."""
        with self.get_connection() as conn:
            if project and project != "all":
                p = project.strip().lower()
                rows = conn.execute(
                    "SELECT * FROM mandatory_specs WHERE project = ? OR project = 'global' ORDER BY id ASC",
                    (p,),
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM mandatory_specs ORDER BY id ASC").fetchall()
            return [MandatorySpec(**dict(row)) for row in rows]

    def delete_spec(self, spec_id: int) -> bool:
        """Delete a mandatory spec by ID."""
        with self.get_connection() as conn:
            cursor = conn.execute("DELETE FROM mandatory_specs WHERE id = ?", (spec_id,))
            return cursor.rowcount > 0

    # ==========================
    # Golden Patterns CRUD
    # ==========================

    def add_golden_pattern(
        self,
        title: str,
        context: str,
        code_snippet: str,
        explanation: str = "",
        project: str = "global",
    ) -> GoldenPattern:
        """Save a battle-tested code snippet that the AI must follow."""
        now = current_iso_time()
        project = project.strip().lower() if project else "global"
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO golden_patterns (project, context, title, code_snippet, explanation, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (project, context.strip().lower(), title.strip(), code_snippet.strip(), explanation.strip(), now),
            )
            return GoldenPattern(
                id=cursor.lastrowid,
                project=project,
                context=context.strip().lower(),
                title=title.strip(),
                code_snippet=code_snippet.strip(),
                explanation=explanation.strip(),
                created_at=now,
            )

    def list_golden_patterns(self, project: Optional[str] = None) -> list[GoldenPattern]:
        """List all golden patterns."""
        with self.get_connection() as conn:
            if project and project != "all":
                p = project.strip().lower()
                rows = conn.execute(
                    "SELECT * FROM golden_patterns WHERE project = ? OR project = 'global' ORDER BY id ASC",
                    (p,),
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM golden_patterns ORDER BY id ASC").fetchall()
            return [GoldenPattern(**dict(row)) for row in rows]

    def delete_golden_pattern(self, pattern_id: int) -> bool:
        """Delete a golden pattern by ID."""
        with self.get_connection() as conn:
            cursor = conn.execute("DELETE FROM golden_patterns WHERE id = ?", (pattern_id,))
            return cursor.rowcount > 0

    # ==========================
    # Experiences (Anti-Patterns & Vaccines)
    # ==========================

    def record_experience(
        self,
        context: str,
        what_failed: str,
        fix_applied: str,
        project: str = "global",
    ) -> Experience:
        """Record a mistake/struggle and the working solution."""
        now = current_iso_time()
        project = project.strip().lower() if project else "global"
        ctx = context.strip().lower()
        failed = what_failed.strip()
        fix = fix_applied.strip()

        with self.get_connection() as conn:
            # Check if an experience with similar context and what_failed exists
            existing = conn.execute(
                """
                SELECT id, recurrence_count FROM experiences 
                WHERE (project = ? OR project = 'global')
                  AND context = ?
                  AND what_failed = ?
                LIMIT 1
                """,
                (project, ctx, failed),
            ).fetchone()

            if existing:
                new_count = existing["recurrence_count"] + 1
                conn.execute(
                    """
                    UPDATE experiences 
                    SET recurrence_count = ?, fix_applied = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (new_count, fix, now, existing["id"]),
                )
                row = conn.execute("SELECT * FROM experiences WHERE id = ?", (existing["id"],)).fetchone()
                return Experience(**dict(row))

            cursor = conn.execute(
                """
                INSERT INTO experiences (project, context, what_failed, fix_applied, recurrence_count, created_at, updated_at)
                VALUES (?, ?, ?, ?, 1, ?, ?)
                """,
                (project, ctx, failed, fix, now, now),
            )
            return Experience(
                id=cursor.lastrowid,
                project=project,
                context=ctx,
                what_failed=failed,
                fix_applied=fix,
                recurrence_count=1,
                created_at=now,
                updated_at=now,
            )

    def list_experiences(self, project: Optional[str] = None) -> list[Experience]:
        """List recorded experiences."""
        with self.get_connection() as conn:
            if project and project != "all":
                p = project.strip().lower()
                rows = conn.execute(
                    "SELECT * FROM experiences WHERE project = ? OR project = 'global' ORDER BY recurrence_count DESC, id DESC",
                    (p,),
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM experiences ORDER BY recurrence_count DESC, id DESC").fetchall()
            return [Experience(**dict(row)) for row in rows]

    def delete_experience(self, exp_id: int) -> bool:
        """Delete an experience by ID."""
        with self.get_connection() as conn:
            cursor = conn.execute("DELETE FROM experiences WHERE id = ?", (exp_id,))
            return cursor.rowcount > 0

    # ==========================
    # Full-Text Search Helpers
    # ==========================

    def _sanitize_fts_query(self, query: str) -> str:
        """Clean and extract alphanumeric search tokens for FTS5."""
        tokens = re.findall(r"\w+", query)
        if not tokens:
            return ""
        # Match tokens using OR or NEAR
        return " OR ".join(tokens)

    def search_experiences(self, query: str, project: str = "global", limit: int = 5) -> list[Experience]:
        """Search experiences using FTS5 with fallback to LIKE."""
        p = project.strip().lower() if project else "global"
        fts_query = self._sanitize_fts_query(query)
        if not fts_query:
            return []

        with self.get_connection() as conn:
            try:
                rows = conn.execute(
                    """
                    SELECT e.* FROM experiences e
                    JOIN experiences_fts fts ON e.id = fts.rowid
                    WHERE experiences_fts MATCH ?
                      AND (e.project = ? OR e.project = 'global')
                    ORDER BY bm25(experiences_fts) ASC, e.recurrence_count DESC
                    LIMIT ?
                    """,
                    (fts_query, p, limit),
                ).fetchall()
                if rows:
                    return [Experience(**dict(r)) for r in rows]
            except sqlite3.OperationalError:
                pass

            # Fallback to LIKE if FTS query syntax error
            tokens = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 2]
            if not tokens:
                return []
            clauses = ["(context LIKE ? OR what_failed LIKE ? OR fix_applied LIKE ?)" for _ in tokens]
            params = []
            for t in tokens:
                params.extend([f"%{t}%", f"%{t}%", f"%{t}%"])
            params.append(p)
            params.append(limit)

            sql = f"""
                SELECT * FROM experiences
                WHERE ({" OR ".join(clauses)})
                  AND (project = ? OR project = 'global')
                ORDER BY recurrence_count DESC
                LIMIT ?
            """
            rows = conn.execute(sql, params).fetchall()
            return [Experience(**dict(r)) for r in rows]

    def search_golden_patterns(self, query: str, project: str = "global", limit: int = 3) -> list[GoldenPattern]:
        """Search golden patterns using FTS5."""
        p = project.strip().lower() if project else "global"
        fts_query = self._sanitize_fts_query(query)
        if not fts_query:
            return []

        with self.get_connection() as conn:
            try:
                rows = conn.execute(
                    """
                    SELECT gp.* FROM golden_patterns gp
                    JOIN golden_patterns_fts fts ON gp.id = fts.rowid
                    WHERE golden_patterns_fts MATCH ?
                      AND (gp.project = ? OR gp.project = 'global')
                    ORDER BY bm25(golden_patterns_fts) ASC
                    LIMIT ?
                    """,
                    (fts_query, p, limit),
                ).fetchall()
                if rows:
                    return [GoldenPattern(**dict(r)) for r in rows]
            except sqlite3.OperationalError:
                pass

            # Fallback
            tokens = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 2]
            if not tokens:
                return []
            clauses = ["(context LIKE ? OR title LIKE ? OR explanation LIKE ?)" for _ in tokens]
            params = []
            for t in tokens:
                params.extend([f"%{t}%", f"%{t}%", f"%{t}%"])
            params.append(p)
            params.append(limit)

            sql = f"""
                SELECT * FROM golden_patterns
                WHERE ({" OR ".join(clauses)})
                  AND (project = ? OR project = 'global')
                LIMIT ?
            """
            rows = conn.execute(sql, params).fetchall()
            return [GoldenPattern(**dict(r)) for r in rows]

    # ==========================
    # Main Consultation Logic
    # ==========================

    def consult(self, context_query: str, project: str = "global") -> ConsultationResult:
        """
        Synthesize rules, mandatory specs, anti-patterns, and golden patterns
        for a task context into an actionable, authoritative guardrail prompt.
        """
        p = project.strip().lower() if project else "global"
        rules = self.list_rules(p)

        # Match specs against context keywords
        all_specs = self.list_specs(p)
        matched_specs = []
        ctx_lower = context_query.lower()
        for spec in all_specs:
            triggers = [t.strip().lower() for t in spec.trigger_pattern.split(",") if t.strip()]
            for trig in triggers:
                if trig in ctx_lower:
                    matched_specs.append(spec)
                    break

        experiences = self.search_experiences(context_query, project=p, limit=4)
        patterns = self.search_golden_patterns(context_query, project=p, limit=2)

        # Build prompt
        formatted_prompt = self._format_prompt(p, context_query, rules, matched_specs, experiences, patterns)

        return ConsultationResult(
            project=p,
            context_query=context_query,
            rules=rules,
            mandatory_specs=matched_specs,
            golden_patterns=patterns,
            experiences=experiences,
            formatted_prompt=formatted_prompt,
        )

    def _format_prompt(
        self,
        project: str,
        context: str,
        rules: list[Rule],
        specs: list[MandatorySpec],
        experiences: list[Experience],
        patterns: list[GoldenPattern],
    ) -> str:
        """Format knowledge into an unmistakable markdown system section."""
        lines = [
            "### 🧠 MEGABRAIN ACTIVE GUARDRAILS & MEMORY",
            f"**Project:** `{project}` | **Context:** `{context}`\n",
        ]

        # 1. Rules
        if rules:
            lines.append("#### 🚨 MANDATORY RULES (STRICT COMPLIANCE REQUIRED):")
            for r in rules:
                lines.append(f"- **[{r.severity}] ({r.category})**: {r.rule}")
            lines.append("")

        # 2. Mandatory specs
        if specs:
            lines.append("#### 🛑 PREREQUISITE SPECIFICATIONS (READ BEFORE CODING):")
            for s in specs:
                lines.append(f"- 📄 File: `{s.spec_path}`")
                lines.append(f"  👉 Directive: **{s.instruction}** (You MUST inspect this file before generating code/designs).")
            lines.append("")

        # 3. Known Traps & Vaccines (Blind spots)
        if experiences:
            lines.append("#### ⚠️ KNOWN AI BLIND SPOTS (DO NOT REPEAT PREVIOUS MISTAKES):")
            for idx, exp in enumerate(experiences, 1):
                rec_badge = f" [Encountered {exp.recurrence_count}x]" if exp.recurrence_count > 1 else ""
                lines.append(f"{idx}. **Context:** `{exp.context}`{rec_badge}")
                lines.append(f"   ❌ **Trap / What Failed:** {exp.what_failed}")
                lines.append(f"   ✅ **Vaccine / Proven Fix:** {exp.fix_applied}")
            lines.append("")

        # 4. Golden Patterns
        if patterns:
            lines.append("#### ⭐ GOLDEN PATTERNS (VERIFIED WORKING IMPLEMENTATION - USE THIS):")
            for pat in patterns:
                lines.append(f"##### {pat.title} (`{pat.context}`)")
                if pat.explanation:
                    lines.append(f"*{pat.explanation}*")
                lines.append("```")
                lines.append(pat.code_snippet)
                lines.append("```\n")

        if not (rules or specs or experiences or patterns):
            lines.append("*(No specific anti-patterns or mandatory specs recorded for this context yet. Proceed following general best practices.)*\n")

        return "\n".join(lines)

    def get_stats(self) -> dict:
        """Return counts of memory items."""
        with self.get_connection() as conn:
            r_count = conn.execute("SELECT count(*) as c FROM rules").fetchone()["c"]
            s_count = conn.execute("SELECT count(*) as c FROM mandatory_specs").fetchone()["c"]
            e_count = conn.execute("SELECT count(*) as c FROM experiences").fetchone()["c"]
            p_count = conn.execute("SELECT count(*) as c FROM golden_patterns").fetchone()["c"]
            return {
                "rules": r_count,
                "mandatory_specs": s_count,
                "experiences": e_count,
                "golden_patterns": p_count,
                "db_path": str(self.db_path),
            }
