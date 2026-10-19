"""Unit tests for MegaBrain MCP Server tools and resources."""

import pytest
from megabrain.server import (
    brain_consult,
    brain_delete_record,
    brain_list_items,
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
def isolated_test_db(monkeypatch, tmp_path):
    """Ensure tests run against an isolated temporary database."""
    from megabrain.db import MegaBrainDB
    test_db = MegaBrainDB(tmp_path / "test.db")
    monkeypatch.setattr("megabrain.server.db", test_db)
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


def test_server_delete_record_and_list_items():
    # Record rule
    brain_record_rule("Temporary rule", project="test_p")
    # Record spec
    brain_require_spec("specs/test.md", "testing", instruction="Inspect test spec", project="test_p")
    # Record experience
    brain_record_experience(context="testing context", what_failed="Mistake X", fix_applied="Solution Y", project="test_p")
    # Record golden pattern
    brain_record_golden_pattern(title="Test Pattern", context="test ctx", code_snippet="print('ok')", project="test_p")

    # Verify listing
    items_all = brain_list_items("all", project="test_p")
    assert "Temporary rule" in items_all
    assert "specs/test.md" in items_all
    assert "Mistake X" in items_all
    assert "Test Pattern" in items_all

    # Delete rule
    del_rule = brain_delete_record("rule", 1)
    assert "Rule #1 deleted successfully" in del_rule

    # Delete non-existent rule
    del_missing = brain_delete_record("rule", 999)
    assert "Rule #999 not found" in del_missing

    # Delete spec
    del_spec = brain_delete_record("spec", 1)
    assert "Prerequisite Spec #1 deleted successfully" in del_spec

    # Delete experience
    del_exp = brain_delete_record("experience", 1)
    assert "Experience #1 deleted successfully" in del_exp

    # Delete golden pattern
    del_pat = brain_delete_record("pattern", 1)
    assert "Golden Pattern #1 deleted successfully" in del_pat

    # Invalid type
    del_invalid = brain_delete_record("invalid_type", 1)
    assert "Unknown item_type" in del_invalid

    # Verify stats after deletion
    stats = brain_stats()
    assert "Rules: 0" in stats
    assert "Mandatory Specs: 0" in stats
    assert "Experiences (Vaccines): 0" in stats
    assert "Golden Patterns: 0" in stats

