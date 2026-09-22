"""Where the code repos this knowledge base documents live — the hub configuration.

A living-doc KB comes in two shapes: `knowledge/` beside one codebase (the
adoption guides' default), or a HUB — one KB documenting several repos it
does not contain (HUB_ADOPTION_GUIDE.md). The hub needs to know its
product repos so `bootstrap` can install the Knowledge: trailer hook and the
session-status hook in each, and `kb-status` can report when one is missing.

Resolution order:
  1. env KB_PRODUCT_REPOS=<path>:<path>
  2. `.living-doc.json` at the KB repo root: {"product_repos": [...], "skill_dir": ".claude/skills/kb"}
  3. none (a single-repo KB: bootstrap installs the gate hook and the skill link only)
"""
from __future__ import annotations

import json
import os
from pathlib import Path

CONFIG_FILE = ".living-doc.json"
DEFAULT_SKILL_DIR = ".claude/skills/kb"


def knowledge_repo() -> Path:
    return Path(__file__).resolve().parents[2]


def _config() -> dict:
    p = knowledge_repo() / CONFIG_FILE
    try:
        return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}
    except json.JSONDecodeError:
        return {}


def product_repos() -> list[Path]:
    env = os.environ.get("KB_PRODUCT_REPOS")
    raw = env.split(":") if env else _config().get("product_repos", [])
    return [Path(p).expanduser() for p in raw if str(p).strip()]


def skill_dir() -> Path:
    return knowledge_repo() / str(_config().get("skill_dir", DEFAULT_SKILL_DIR))
