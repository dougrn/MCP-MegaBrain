"""Unit tests for MegaBrain MCP Server tools and resources."""

import pytest
from megabrain.server import (
    brain_consult,
    brain_list_rules,
    brain_record_experience,
    brain_record_golden_pattern,
    brain_record_rule,
    brain_require_spec,
    brain_stats,
    db,
    resource_rules,
    resource_stats,
)


@pytest.fixture(autouse=True)
def clean_database():
    """Ensure a clean test state before each test."""
    with db.get_connection() as conn:
        conn.execute("DELETE FROM rules;")
        conn.execute("DELETE FROM mandatory_specs;")
        conn.execute("DELETE FROM experiences;")
        conn.execute("DELETE FROM golden_patterns;")
    yield


def test_server_record_rule_and_consult():
    msg = brain_record_rule("Use strict types", category="style", project="myapp", severity="CRITICAL")
    assert "Rule registered" in msg
    assert "myapp" in msg

    consult_output = brain_consult("general code refactor", project="myapp")
    assert "Use strict types" in consult_output
    assert "[CRITICAL] (style)" in consult_output


def test_server_require_spec():
    msg = brain_require_spec("specs/auth.md", "auth, login, jwt", "Read JWT security spec", project="myapp")
    assert "Prerequisite Spec registered" in msg

    consult_output = brain_consult("create login authentication controller", project="myapp")
    assert "specs/auth.md" in consult_output
    assert "Read JWT security spec" in consult_output


def test_server_record_experience_with_snippet():
    msg = brain_record_experience(
        context="python sqlite fts5",
        what_failed="FTS5 query failed with syntax error",
        fix_applied="Sanitize query tokens into OR statements",
        project="global",
        verified_snippet="tokens = re.findall(r'\\w+', query); return ' OR '.join(tokens)",
    )
    assert "Experience recorded successfully" in msg
    assert "Golden Pattern" in msg

    consult_output = brain_consult("sqlite fts5 query search", project="global")
    assert "FTS5 query failed with syntax error" in consult_output
    assert "Sanitize query tokens into OR statements" in consult_output
    assert "tokens = re.findall" in consult_output


def test_server_stats_and_resources():
    brain_record_rule("Rule A", project="global")
    stats_msg = brain_stats()
    assert "Rules: 1" in stats_msg

    res_r = resource_rules()
    assert "Rule A" in res_r

    res_s = resource_stats()
    assert "Rules: 1" in res_s


def test_server_list_rules():
    brain_record_rule("Rule 1", project="p1")
    brain_record_rule("Rule 2", project="p2")

    p1_rules = brain_list_rules("p1")
    assert "Rule 1" in p1_rules
    assert "Rule 2" not in p1_rules
