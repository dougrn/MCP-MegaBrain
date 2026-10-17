"""Unit tests for the CLI commands."""

import subprocess
import sys


def test_cli_help():
    result = subprocess.run([sys.executable, "-m", "megabrain.cli", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "MegaBrain" in result.stdout
    assert "consult" in result.stdout
    assert "record-rule" in result.stdout


def test_cli_contract():
    result = subprocess.run([sys.executable, "-m", "megabrain.cli", "contract", "--raw"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "MEGABRAIN AGENT CONTRACT" in result.stdout
    assert "MANDATORY PRE-FLIGHT CHECK" in result.stdout
