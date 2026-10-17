"""Configuration and path management for MCP-MegaBrain."""

import os
from pathlib import Path

# Directory where MegaBrain stores persistent data
DEFAULT_DIR = Path.home() / ".megabrain"
MEGABRAIN_DIR = Path(os.environ.get("MEGABRAIN_DIR", str(DEFAULT_DIR)))

# Database file path
DEFAULT_DB_PATH = MEGABRAIN_DIR / "megabrain.db"
MEGABRAIN_DB_PATH = Path(os.environ.get("MEGABRAIN_DB_PATH", str(DEFAULT_DB_PATH)))


def ensure_data_dir() -> Path:
    """Ensure that the data directory exists and return it."""
    MEGABRAIN_DIR.mkdir(parents=True, exist_ok=True)
    return MEGABRAIN_DIR


def get_db_path() -> Path:
    """Ensure directory exists and return the SQLite database path."""
    ensure_data_dir()
    return MEGABRAIN_DB_PATH
