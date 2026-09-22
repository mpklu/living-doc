#!/usr/bin/env python3
"""Install (or report) everything enforcement depends on that git does not version.

WHY (2026-09-21): `.git/hooks/` is per-clone. A fresh clone of this repo lost
the commit gate; a fresh clone of MacPractice/MPXServer lost the Knowledge:
trailer check; and the `/kb` skill + session status existed only inside this
repo's `.claude/`, while the agents who most need the write path work in the
product repos. Nothing said so until a violation slipped through. This makes
the installation one idempotent command and its absence visible (kb-status
runs the --check).

What it installs:
  1. this repo:      .git/hooks/pre-commit → scripts/pre-commit-gate
  2. product repos:  .git/hooks/commit-msg → scripts/check-trailer (touch-verifying)
  3. product repos:  .claude/settings.local.json ← SessionStart hook → scripts/kb-status
                     (settings.local.json is machine-local and git-ignored there:
                     no noise in the product repo's working tree)
  4. user level:     ~/.claude/skills/kb → this repo's skill dir (symlink; `.living-doc.json`
                     `skill_dir`, default .claude/skills/kb) so /kb exists in every session.
                     Skipped with a note when the repo ships no such skill.

Product repos come from `.living-doc.json` / KB_PRODUCT_REPOS (kb_paths.py); a
single-repo KB lists none and gets the gate hook + skill link only.

Usage:
    bootstrap            # install what is missing, report each action
    bootstrap --check    # report only; exit 1 if anything is missing (kb-status uses this)
    KB_PRODUCT_REPOS=/a:/b bootstrap
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import kb_paths

STATUS_CMD_TMPL = 'cd "{kb}" && scripts/kb-status 2>/dev/null || true'


def _kb_status_hook(kb: Path) -> dict:
    return {"hooks": [{"type": "command", "command": STATUS_CMD_TMPL.format(kb=kb),
                       "timeout": 30, "statusMessage": "Knowledge-base status…"}]}


def check(kb: Path, repos: list[Path], home: Path) -> list[str]:
    """Human-readable list of missing pieces; empty = fully installed."""
    missing: list[str] = []
    hook = kb / ".git" / "hooks" / "pre-commit"
    if not (hook.is_file() and "pre-commit-gate" in hook.read_text(encoding="utf-8", errors="ignore")):
        missing.append(f"commit gate hook missing in {kb.name} (.git/hooks/pre-commit)")
    for r in repos:
        if not (r / ".git").exists():
            missing.append(f"product repo not found: {r}")
            continue
        cm = r / ".git" / "hooks" / "commit-msg"
        if not (cm.is_file() and "check-trailer" in cm.read_text(encoding="utf-8", errors="ignore")):
            missing.append(f"Knowledge: trailer hook missing in {r.name} (.git/hooks/commit-msg)")
        sl = r / ".claude" / "settings.local.json"
        try:
            cfg = json.loads(sl.read_text(encoding="utf-8")) if sl.is_file() else {}
        except json.JSONDecodeError:
            cfg = {}
        starts = json.dumps(cfg.get("hooks", {}).get("SessionStart", []))
        if "kb-status" not in starts:
            missing.append(f"kb-status SessionStart hook missing in {r.name} (.claude/settings.local.json)")
    link = home / ".claude" / "skills" / "kb"
    if (kb_paths.skill_dir() / "SKILL.md").is_file() and not (link.is_dir() and (link / "SKILL.md").is_file()):
        missing.append("user-level /kb skill missing (~/.claude/skills/kb)")
    return missing


def install(kb: Path, repos: list[Path], home: Path) -> int:
    rc = 0
    hook = kb / ".git" / "hooks" / "pre-commit"
    if (kb / ".git").exists():
        hook.parent.mkdir(parents=True, exist_ok=True)
        want = "#!/bin/sh\nexec scripts/pre-commit-gate\n"
        if not hook.is_file() or hook.read_text(encoding="utf-8", errors="ignore") != want:
            hook.write_text(want, encoding="utf-8"); hook.chmod(0o755)
            print(f"installed {hook}")
    wrapper = kb / "scripts" / "check-trailer"
    for r in repos:
        if not (r / ".git").exists():
            print(f"⚠️  product repo not found, skipped: {r}"); rc = 1
            continue
        cm = r / ".git" / "hooks" / "commit-msg"
        want = f'#!/bin/sh\nexec "{wrapper}" --knowledge-repo "{kb}" --commit-msg-file "$1"\n'
        if not cm.is_file() or cm.read_text(encoding="utf-8", errors="ignore") != want:
            cm.parent.mkdir(parents=True, exist_ok=True)
            cm.write_text(want, encoding="utf-8"); cm.chmod(0o755)
            print(f"installed {cm}")
        sl = r / ".claude" / "settings.local.json"
        try:
            cfg = json.loads(sl.read_text(encoding="utf-8")) if sl.is_file() else {}
        except json.JSONDecodeError:
            print(f"⚠️  {sl} is not valid JSON; not touching it"); rc = 1
            continue
        starts = cfg.setdefault("hooks", {}).setdefault("SessionStart", [])
        if "kb-status" not in json.dumps(starts):
            starts.append(_kb_status_hook(kb))
            sl.parent.mkdir(parents=True, exist_ok=True)
            sl.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
            print(f"added kb-status SessionStart hook to {sl}")
    link = home / ".claude" / "skills" / "kb"
    target = kb_paths.skill_dir()
    if not (target / "SKILL.md").is_file():
        print(f"(no skill at {target.relative_to(kb)}; skill link skipped)")
    elif link.is_symlink() and link.resolve() == target.resolve():
        pass
    elif link.exists() or link.is_symlink():
        print(f"⚠️  {link} exists and is not a link to {target}; leaving it"); rc = 1
    else:
        link.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(target, link)
        print(f"linked {link} -> {target}")
    left = check(kb, repos, home)
    if left:
        for m in left:
            print(f"⚠️  still missing: {m}")
        return 1
    print("✅ bootstrap: gate hook" + (" · trailer hooks · session status" if repos else "") + " · /kb skill — installed.")
    return rc


def cli_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Install or check the un-versioned enforcement pieces.")
    ap.add_argument("--check", action="store_true", help="report only; exit 1 if anything is missing")
    ap.add_argument("--knowledge-repo", default=None)
    ap.add_argument("--home", default=None, help="override $HOME (tests)")
    args = ap.parse_args(argv)
    kb = Path(args.knowledge_repo).resolve() if args.knowledge_repo else kb_paths.knowledge_repo()
    home = Path(args.home) if args.home else Path.home()
    repos = kb_paths.product_repos()
    if args.check:
        missing = check(kb, repos, home)
        if missing:
            for m in missing:
                print(f"⚠️  {m}")
            print("   Fix: scripts/bootstrap")
            return 1
        print("✅ bootstrap --check: all enforcement pieces installed.")
        return 0
    return install(kb, repos, home)


if __name__ == "__main__":
    sys.exit(cli_main())
