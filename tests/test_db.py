"""Tests for SQLite database storage and FTS5 search."""

import pytest
from megabrain.db import MegaBrainDB


@pytest.fixture
def db():
    """Create an isolated in-memory MegaBrain database."""
    return MegaBrainDB(":memory:")


def test_db_initialization(db):
    stats = db.get_stats()
    assert stats["rules"] == 0
    assert stats["mandatory_specs"] == 0
    assert stats["experiences"] == 0
    assert stats["golden_patterns"] == 0


def test_add_and_list_rules(db):
    r1 = db.add_rule("Strict English only", category="language", project="ecommerce", severity="CRITICAL")
    r2 = db.add_rule("Never commit without confirmation", category="git", project="global", severity="HIGH")

    assert r1.id is not None
    assert r1.rule == "Strict English only"

    # Filtered by project should include global + project rules
    ecom_rules = db.list_rules("ecommerce")
    assert len(ecom_rules) == 2
    assert ecom_rules[0].severity == "CRITICAL"  # CRITICAL comes first

    # Other project should only see global
    other_rules = db.list_rules("other_app")
    assert len(other_rules) == 1
    assert other_rules[0].rule == "Never commit without confirmation"


def test_mandatory_specs_matching(db):
    spec = db.add_spec(
        spec_path="specs/design-tokens.md",
        trigger_pattern="design, ui, layout, componentes",
        instruction="Read design tokens before styling.",
        project="portal",
    )
    assert spec.id is not None

    # Matching query
    res = db.consult(context_query="Refactor the navbar UI layout", project="portal")
    assert len(res.mandatory_specs) == 1
    assert "specs/design-tokens.md" in res.formatted_prompt
    assert "Read design tokens before styling." in res.formatted_prompt

    # Non-matching query
    res_db = db.consult(context_query="Optimize MySQL index", project="portal")
    assert len(res_db.mandatory_specs) == 0


def test_experience_recording_and_recurrence(db):
    # First time recording
    exp1 = db.record_experience(
        context="php mysql",
        what_failed="Called set_charset on uninitialized connection",
        fix_applied="Pass charset=utf8mb4 inside DSN string",
        project="global",
    )
    assert exp1.recurrence_count == 1

    # Second time with same context & what_failed -> increments recurrence
    exp2 = db.record_experience(
        context="php mysql",
        what_failed="Called set_charset on uninitialized connection",
        fix_applied="Updated: Always pass charset=utf8mb4 in DSN",
        project="global",
    )
    assert exp2.id == exp1.id
    assert exp2.recurrence_count == 2
    assert exp2.fix_applied == "Updated: Always pass charset=utf8mb4 in DSN"

    # Consult surfaces the vaccine
    res = db.consult(context_query="php mysql connection", project="any_project")
    assert len(res.experiences) == 1
    assert "Encountered 2x" in res.formatted_prompt
    assert "pass charset=utf8mb4 in DSN" in res.formatted_prompt


def test_golden_patterns_fts(db):
    db.add_golden_pattern(
        title="PHP PDO MySQL Connection",
        context="php mysql pdo connection",
        code_snippet="$pdo = new PDO('mysql:host=localhost;dbname=test;charset=utf8mb4', $u, $p);",
        explanation="Guarantees UTF-8 encoding and PDO error exceptions",
        project="global",
    )

    res = db.consult(context_query="how to connect to mysql in php", project="my_project")
    assert len(res.golden_patterns) == 1
    assert "PHP PDO MySQL Connection" in res.formatted_prompt
    assert "$pdo = new PDO" in res.formatted_prompt


def test_delete_operations(db):
    r = db.add_rule("Test rule", project="test")
    assert len(db.list_rules("test")) == 1
    assert db.delete_rule(r.id) is True
    assert len(db.list_rules("test")) == 0

    s = db.add_spec("specs/a.md", "a", project="test")
    assert db.delete_spec(s.id) is True

    e = db.record_experience("ctx", "failed", "fix", project="test")
    assert db.delete_experience(e.id) is True


def test_project_normalization_and_isolation(db):
    from megabrain.db import normalize_project

    assert normalize_project("dougrn/ldg") == "ldg"
    assert normalize_project("c:\\users\\dougl\\desktop\\ldg") == "ldg"
    assert normalize_project("global") == "global"
    assert normalize_project("all") == "all"
    assert normalize_project("") == "global"
    assert normalize_project(None) == "global"

    # Add rule to LDG with owner prefix
    r = db.add_rule("LDG rule only", category="architecture", project="dougrn/ldg")
    assert r.project == "ldg"

    # LDG sees it
    assert len(db.list_rules("ldg")) == 1
    assert len(db.list_rules("dougrn/ldg")) == 1

    # Unrelated project does NOT see it
    assert len(db.list_rules("buscapjota")) == 0
    res = db.consult(context_query="google places api", project="buscapjota")
    assert "LDG rule only" not in res.formatted_prompt
