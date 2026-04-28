#!/usr/bin/env python3
"""Drift check for the living-documentation methodology.

Reads the article-mapping table from CLAUDE.md and verifies that PRs touching
mapped code paths also touch the corresponding articles. Enforces the
same-task rule at PR-review time, complementing the agent's discipline at
write-time.

Inputs (env vars):
    CLAUDE_MD_PATH    — path to CLAUDE.md (default: CLAUDE.md)
    KNOWLEDGE_DIR     — path to knowledge directory (default: knowledge)
    BASE_REF          — base ref to diff against (default: $GITHUB_BASE_REF
                        or "main")
    FAIL_ON_VIOLATION — "true" or "false" (default: "true")
    GITHUB_OUTPUT     — path to the GitHub Actions output file (set by GitHub)

Outputs (via $GITHUB_OUTPUT, when set):
    violations — count of violations
    report     — markdown-formatted report

Exit codes:
    0  — no violations, or violations found and FAIL_ON_VIOLATION=false
    1  — violations found and FAIL_ON_VIOLATION=true
    2  — configuration / parse error
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MappingRow:
    """One row of the article-mapping table."""

    code_pattern: str  # e.g., "src/workflows/*.py" or "the LLM agent"
    article_path: str  # e.g., "knowledge/concepts/x.md"


def parse_article_mapping(claude_md_text: str) -> list[MappingRow]:
    """Parse the article-mapping table from CLAUDE.md text.

    Looks for a Markdown table where:
    - The header row contains "When you change" and "Update this article"
      (case-insensitive).
    - Subsequent rows have two cells; the second cell contains a backticked
      path ending in .md.

    Returns an empty list if no mapping table is found, or if rows are
    malformed.
    """
    rows: list[MappingRow] = []
    lines = claude_md_text.splitlines()

    in_table = False
    for i, line in enumerate(lines):
        # Detect the header row of the mapping table.
        lower = line.lower()
        if "when you change" in lower and "update this article" in lower:
            in_table = True
            continue
        if in_table:
            # The line right after the header is the separator (| --- | --- |)
            if re.match(r"\s*\|[\s\-|]+\|\s*$", line):
                continue
            # End of table = blank line or non-table line
            if not line.strip().startswith("|"):
                in_table = False
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 2:
                continue
            code_pattern = cells[0]
            article_cell = cells[1]
            article_match = re.search(r"`([^`]+\.md)`", article_cell)
            if not article_match:
                continue
            rows.append(
                MappingRow(
                    code_pattern=code_pattern,
                    article_path=article_match.group(1),
                )
            )
    return rows


def get_changed_files(base_ref: str) -> list[str]:
    """Return the list of files changed between base_ref and HEAD."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        # Try fallback: maybe base_ref was provided as a remote ref
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", base_ref, "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError:
            print(f"::error::git diff failed: {e.stderr}", file=sys.stderr)
            sys.exit(2)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def code_pattern_matches_files(
    code_pattern: str, changed_files: list[str]
) -> list[str]:
    """Determine which changed files match a mapping row's code pattern.

    The pattern can be:
    - A glob-like path (contains "/", "*", or ends in ".py" / similar) — match
      via Python's fnmatch.
    - A natural-language description (no path-like characters) — match by
      keyword: any changed file whose path contains any non-trivial word from
      the description.

    Returns the subset of changed_files that match.
    """
    import fnmatch

    pattern = code_pattern.strip().strip("`")

    looks_like_path = "/" in pattern or "*" in pattern or pattern.endswith(
        (".py", ".ts", ".tsx", ".js", ".go", ".rs", ".rb", ".md", ".yml", ".yaml")
    )

    if looks_like_path:
        return [f for f in changed_files if fnmatch.fnmatch(f, pattern)]

    # Natural-language description fallback: match by keyword.
    keywords = [
        w.lower()
        for w in re.findall(r"\b\w{4,}\b", pattern)
        if w.lower() not in {"this", "that", "with", "when", "from", "into", "code"}
    ]
    if not keywords:
        return []
    matches: list[str] = []
    for f in changed_files:
        f_lower = f.lower()
        if any(kw in f_lower for kw in keywords):
            matches.append(f)
    return matches


def check_drift(
    mapping: list[MappingRow],
    changed_files: list[str],
    knowledge_dir: str,
) -> list[dict]:
    """Identify violations: rows where code matched but article didn't change.

    Returns a list of violation dicts, each with:
        code_pattern   — the mapping row's code pattern
        article_path   — the expected article path
        matched_files  — which changed files matched the code pattern
    """
    violations: list[dict] = []
    changed_set = {f for f in changed_files}

    for row in mapping:
        matched = code_pattern_matches_files(row.code_pattern, changed_files)
        if not matched:
            continue
        # Normalize article path; allow it to be relative or knowledge-rooted.
        article = row.article_path
        if not article.startswith(knowledge_dir + "/") and not article.startswith(
            "/"
        ):
            article = f"{knowledge_dir}/{article}"
        if article in changed_set or article.lstrip("/") in changed_set:
            continue
        violations.append(
            {
                "code_pattern": row.code_pattern,
                "article_path": article,
                "matched_files": matched,
            }
        )
    return violations


def format_report(violations: list[dict], rows_total: int) -> str:
    """Format a markdown report of the check results."""
    if not violations:
        return (
            "✅ **Living Docs drift check passed.** "
            f"All {rows_total} mapped code paths that were touched in this PR "
            "have corresponding article updates."
        )

    lines = [
        "⚠️ **Living Docs drift check — same-task rule violations detected.**",
        "",
        f"This PR touches code paths listed in `CLAUDE.md`'s article-mapping "
        f"table, but does not update the corresponding articles. The "
        f"living-documentation methodology requires articles to be updated "
        f"in the **same task** as the code change.",
        "",
        "### Violations",
        "",
    ]
    for v in violations:
        lines.append(f"- **{v['code_pattern']}** → expected article: "
                     f"`{v['article_path']}`")
        for f in v["matched_files"][:5]:
            lines.append(f"    - changed file: `{f}`")
        if len(v["matched_files"]) > 5:
            lines.append(
                f"    - ... and {len(v['matched_files']) - 5} more changed file(s)"
            )
    lines.extend(
        [
            "",
            "### What to do",
            "",
            "1. **Capture first, refine second.** Add the missing article "
            "update(s) to this PR. An imperfect article is strictly better "
            "than a missed one — the reviewer can refine on review.",
            "2. If the article doesn't yet exist for one of the paths above, "
            "write the first thin article in the same PR (~200 words). See "
            "`CLAUDE.md` for placement guidance.",
            "3. Append an entry to `knowledge/log.md` listing what was touched.",
            "",
            "_If the matching is wrong (the code pattern is too broad or the "
            "article truly doesn't apply to this change), update the "
            "`CLAUDE.md` mapping table to fix the pattern — that's also a "
            "valid resolution._",
        ]
    )
    return "\n".join(lines)


def emit_output(name: str, value: str) -> None:
    """Write a value to GitHub Actions outputs, or stdout if not in Actions."""
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a", encoding="utf-8") as f:
            # Multiline-safe output via heredoc syntax
            delim = "EOF_DRIFT_CHECK"
            f.write(f"{name}<<{delim}\n{value}\n{delim}\n")
    else:
        print(f"::{name}::{value}")


def main() -> int:
    claude_md_path = os.environ.get("CLAUDE_MD_PATH", "CLAUDE.md")
    knowledge_dir = os.environ.get("KNOWLEDGE_DIR", "knowledge")
    base_ref = (
        os.environ.get("BASE_REF")
        or os.environ.get("GITHUB_BASE_REF")
        or "main"
    )
    fail_on_violation = (
        os.environ.get("FAIL_ON_VIOLATION", "true").strip().lower() == "true"
    )

    claude_md = Path(claude_md_path)
    if not claude_md.exists():
        print(
            f"::error::CLAUDE.md not found at {claude_md_path}. "
            "Skipping drift check (no mapping to verify against).",
            file=sys.stderr,
        )
        emit_output("violations", "0")
        emit_output(
            "report",
            f"⚠️ Living Docs drift check skipped — `{claude_md_path}` not "
            "found in this repository.",
        )
        return 0

    mapping = parse_article_mapping(claude_md.read_text(encoding="utf-8"))
    if not mapping:
        emit_output("violations", "0")
        emit_output(
            "report",
            "ℹ️ Living Docs drift check found no article-mapping table in "
            f"`{claude_md_path}`. Either the table hasn't been populated yet "
            "(brownfield retrofit, early days) or the table format isn't "
            "recognized. No violations reported.",
        )
        return 0

    changed_files = get_changed_files(base_ref)
    if not changed_files:
        emit_output("violations", "0")
        emit_output("report", "✅ No files changed; nothing to check.")
        return 0

    violations = check_drift(mapping, changed_files, knowledge_dir)
    report = format_report(violations, len(mapping))

    emit_output("violations", str(len(violations)))
    emit_output("report", report)

    print(report)

    if violations and fail_on_violation:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
