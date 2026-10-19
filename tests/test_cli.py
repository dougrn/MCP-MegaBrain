"""Unit tests for the CLI commands."""

import subprocess
import sys


def test_cli_help():
    result = subprocess.run([sys.executable, "-m", "megabrain.cli", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "MegaBrain" in result.stdout
    assert "consult" in result.stdout
    assert "record-rule" in result.stdout
    assert "delete" in result.stdout


def test_cli_contract():
    result = subprocess.run([sys.executable, "-m", "megabrain.cli", "contract", "--raw"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "MEGABRAIN AGENT CONTRACT" in result.stdout
    assert "MANDATORY PRE-FLIGHT CHECK" in result.stdout


def test_cli_record_and_delete(tmp_path):
    import os
    env = os.environ.copy()
    env["MEGABRAIN_DB_PATH"] = str(tmp_path / "cli_test.db")

    # Add a rule
    add_res = subprocess.run(
        [sys.executable, "-m", "megabrain.cli", "record-rule", "CLI Rule to delete"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert add_res.returncode == 0
    assert "Rule added" in add_res.stdout

    # Delete the rule
    del_res = subprocess.run(
        [sys.executable, "-m", "megabrain.cli", "delete", "rule", "1"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert del_res.returncode == 0
    assert "deleted successfully" in del_res.stdout

    # Delete again (not found)
    del_res2 = subprocess.run(
        [sys.executable, "-m", "megabrain.cli", "delete", "rule", "1"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert del_res2.returncode == 0
    assert "not found" in del_res2.stdout

