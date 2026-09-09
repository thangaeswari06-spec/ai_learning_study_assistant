"""
utils/json_handler.py
----------------------
Generic helpers to read/write JSON files.
Every module in this project (memory, rag, tools) goes through
these two functions so that file-handling / error-handling logic
lives in exactly one place.
"""

import json
import os


def load_json(path: str, default=None):
    """
    Load JSON data from `path`.
    If the file does not exist or is corrupted, return `default`
    (or an empty dict if no default is supplied) instead of crashing.
    """
    if default is None:
        default = {}

    if not os.path.exists(path):
        # Make sure the folder exists and create an empty file
        os.makedirs(os.path.dirname(path), exist_ok=True)
        save_json(path, default)
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return default
            return json.loads(content)
    except (json.JSONDecodeError, OSError):
        print(f"[WARN] Could not read '{path}', using default value.")
        return default


def save_json(path: str, data) -> None:
    """Write `data` to `path` as nicely-indented JSON."""
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
