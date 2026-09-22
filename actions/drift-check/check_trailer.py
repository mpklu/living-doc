#!/usr/bin/env python3
"""Cross-repo same-task enforcement: the `Knowledge:` commit trailer hook.

THE GAP THIS CLOSES: drift-check guards the knowledge repo, but the
same-task rule's most dangerous violations happen in the PRODUCT repos —
where the code lives and drift-check is blind. The documented convention
("name the touched article in the product commit via a `Knowledge:`
trailer") has historically been enforced by nothing but discipline.

Runs in a PRODUCT repo (as a `commit-msg` hook, or standalone):

  1. Collect the staged paths (or `--paths` for testing).
  2. Match them against the KNOWLEDGE repo's article `affects:` globs
     (same matcher as drift-check: `**` recursion, brace alternation,
     force-glob — plus each path is also tried with the product repo's
     basename prefixed, so `ProductRepo/**/x` globs work from inside).
     `external:` affects entries match by repo name: an entry containing
     this repo's basename maps ALL staged changes to that article.
  3. If anything matched, the commit message must contain either a
     `Knowledge: <article-or-note>` trailer or an explicit
     `no knowledge impact: <reason>` line. Otherwise: block (exit 1)
     with the expected article list and a paste-ready trailer.

  4. (v2, 2026-09-21) The trailer must name at least one article that
     EXISTS under the knowledge dir and was actually TOUCHED — any of:
     dirty in the knowledge repo's working tree (staged or not), committed
     there within `--touch-window-hours` (default 24), or `updated:` set to
     today. v1 accepted any non-empty trailer, so `Knowledge: concepts/x.md`
     satisfied the hook without anyone opening x.md — the one enforcement
     layer that ran on the honour system. `--names-only` restores v1.

Deliberately helpful, not hostile: the printed article list is guidance
(you may name a different article than the matcher predicted, as long as
you touched it), `--warn-only` never blocks, and `git commit --no-verify`
remains the escape hatch (product repos typically lack a CI net behind
it — the trade-off is documented, not hidden).

Usage:
  check-trailer --knowledge-repo ~/src/knowledge-hub                 # staged set, message from --msg-text/--commit-msg-file
  check-trailer --knowledge-repo P --commit-msg-file .git/COMMIT_EDITMSG
  check-trailer --knowledge-repo P --paths Source/Foo.m --msg-text "fix"   # testing
  check-trailer --install --knowledge-repo P    # write .git/hooks/commit-msg in THIS (product) repo

Co-located with drift_check.py (reuses its parser + matcher).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import re
import subprocess
import sys
from pathlib import Path

from drift_check import (
    _expand_braces,
    _glob_to_regex,
    parse_articles_affects,
)
from validate_articles import parse_frontmatter

TRAILER_RE_TMPL = r"(?mi)^{trailer}\s*:\s*\S"
TRAILER_VALUE_RE_TMPL = r"(?mi)^{trailer}\s*:\s*(.+)$"
NO_IMPACT_RE = re.compile(r"(?i)no knowledge impact\s*:")
MD_PATH_RE = re.compile(r"[\w./\-+ ]*?[\w\-+]+\.md")


def trailer_article_paths(
    body: str, trailer: str, knowledge_repo: Path, knowledge_dir: str
) -> tuple[list[Path], list[str]]:
    """Resolve the `.md` tokens named in every trailer line.

    Returns (existing article paths, unresolvable tokens). Accepts
    `concepts/x.md`, `knowledge/concepts/x.md`, backticked, or several
    per line separated by commas/spaces; free text without a `.md` token
    resolves to nothing."""
    kdir = knowledge_repo / knowledge_dir
    found: list[Path] = []
    missing: list[str] = []
    for m in re.finditer(TRAILER_VALUE_RE_TMPL.format(trailer=re.escape(trailer)), body):
        value = m.group(1).replace("`", " ")
        for tok in MD_PATH_RE.findall(value):
            tok = tok.strip().strip(",;")
            if not tok:
                continue
            rel = tok
            prefix = knowledge_dir.rstrip("/") + "/"
            if rel.startswith(prefix):
                rel = rel[len(prefix):]
            candidate = kdir / rel
            if candidate.is_file():
                if candidate not in found:
                    found.append(candidate)
            else:
                missing.append(tok)
    return found, missing


def _git(repo: Path, *args: str) -> str | None:
    try:
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True, text=True, check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None


def touch_evidence(
    article: Path, knowledge_repo: Path, window_hours: int
) -> str | None:
    """Why we believe this article was touched in the current task, or None.

    Three independent signals, cheapest-to-strongest: uncommitted change in
    the knowledge repo, a commit within the window, or `updated:` == today
    (bump-updated sets it on staged articles; a same-day KB commit older
    than the window still carries it)."""
    try:
        rel = article.relative_to(knowledge_repo).as_posix()
    except ValueError:
        rel = str(article)
    dirty = _git(knowledge_repo, "status", "--porcelain", "--untracked-files=all", "--", rel)
    if dirty and dirty.strip():
        return "uncommitted change in knowledge repo"
    recent = _git(knowledge_repo, "log", "-1", f"--since={window_hours} hours ago",
                  "--format=%h", "--", rel)
    if recent and recent.strip():
        return f"committed {recent.strip()} within {window_hours}h"
    fm = parse_frontmatter(article) or {}
    if str(fm.get("updated", "")) == _dt.date.today().isoformat():
        return "updated: is today"
    return None


def staged_paths() -> list[str]:
    try:
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            capture_output=True, text=True, check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"check-trailer: git diff failed: {exc}")
    return [p for p in out.splitlines() if p.strip()]


def match_articles(
    knowledge_repo: Path, knowledge_dir: str, repo_name: str, paths: list[str]
) -> dict[str, list[str]]:
    """article -> matched paths, using glob affects (+ repo-name-prefixed
    candidates) and repo-name matching for `external:` entries."""
    kdir = knowledge_repo / knowledge_dir
    matched: dict[str, list[str]] = {}

    # Glob affects (external: already skipped by parse_articles_affects).
    rows = parse_articles_affects(str(kdir))
    candidates = {p: [p, f"{repo_name}/{p}"] for p in paths}
    for row in rows:
        regexes = [_glob_to_regex(v) for v in _expand_braces(row.code_pattern)]
        hits = [
            p for p, cands in candidates.items()
            if any(re.match(rx, c) for rx in regexes for c in cands)
        ]
        if hits:
            matched.setdefault(row.article_path, []).extend(
                h for h in hits if h not in matched.get(row.article_path, [])
            )

    # external: entries — repo-level mapping by name. Match against PATH
    # SEGMENTS, not raw substring: "MacPractice" must match the /MacPractice/
    # segment of an entry, but NOT the host "gitlab.macpractice.net" — the
    # first field run produced 12 bogus whole-repo mappings exactly that way.
    # Dotted segments (hosts, filenames) are excluded from comparison.
    if paths:
        rn = repo_name.lower()
        for article in sorted(kdir.rglob("*.md")):
            fm = parse_frontmatter(article)
            if not fm:
                continue
            for entry in fm.get("affects", []) or []:
                if not (isinstance(entry, str) and entry.startswith("external:")):
                    continue
                tail = entry[len("external:"):].strip()
                segments = [
                    s.lower() for s in re.split(r"[/\s]+", tail)
                    if s and "." not in s
                ]
                if rn in segments:
                    matched.setdefault(str(article), []).append(
                        f"(whole repo: external match on '{repo_name}')"
                    )
                    break
    return matched


def install_hook(knowledge_repo: Path) -> int:
    git_dir = Path(".git")
    if not git_dir.is_dir():
        print("check-trailer --install: run from the PRODUCT repo's root "
              "(no .git here).", file=sys.stderr)
        return 1
    wrapper = knowledge_repo / "scripts" / "check-trailer"
    if not wrapper.exists():
        print(f"check-trailer --install: {wrapper} not found — is "
              f"{knowledge_repo} the knowledge repo?", file=sys.stderr)
        return 1
    hook = git_dir / "hooks" / "commit-msg"
    hook.write_text(
        "#!/bin/sh\n"
        f'exec "{wrapper}" --knowledge-repo "{knowledge_repo}" '
        '--commit-msg-file "$1"\n',
        encoding="utf-8",
    )
    hook.chmod(0o755)
    print(f"installed {hook} -> {wrapper}")
    return 0


def _rel(path: str | Path, knowledge_repo: Path) -> str:
    try:
        return str(Path(path).relative_to(knowledge_repo))
    except ValueError:
        return str(path)


def verify_touched(
    args, body: str, knowledge_repo: Path, matched: dict[str, list[str]]
) -> int:
    """v2 gate: the trailer's articles must exist and show touch evidence."""
    named, missing = trailer_article_paths(
        body, args.trailer, knowledge_repo, args.knowledge_dir
    )
    untouched = []
    for article in named:
        if touch_evidence(article, knowledge_repo, args.touch_window_hours) is None:
            untouched.append(article)
    if named and not missing and not untouched:
        return 0

    print(f"⚠️  `{args.trailer}:` trailer present, but it does not point at a "
          f"touched article.")
    if not named and not missing:
        print("   The trailer names no `.md` path under "
              f"{args.knowledge_dir}/ — a note is not an article update.")
    for tok in missing:
        print(f"   • not found: {tok}")
    for article in untouched:
        print(f"   • unchanged: {_rel(article, knowledge_repo)} — not dirty in "
              f"the knowledge repo, no commit in the last "
              f"{args.touch_window_hours}h, `updated:` is not today")
    print("\n   Same-task rule: edit the article now (or commit it in the "
          "knowledge repo), then re-run this commit.")
    if matched:
        print("   Articles the matcher expected for these paths:")
        for article in sorted(matched):
            print(f"     • {_rel(article, knowledge_repo)}")
    print("   …or, if genuinely doc-irrelevant:\n     no knowledge impact: <reason>")
    print("   Name-only check (v1 behaviour): --names-only · "
          "Bypass (discouraged): git commit --no-verify")
    return 0 if args.warn_only else 1


def cli_main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Require a Knowledge: trailer on product-repo commits "
                    "that touch article-mapped code paths."
    )
    ap.add_argument("--knowledge-repo", required=True,
                    help="path to the knowledge repo (holds knowledge/ + scripts/)")
    ap.add_argument("--knowledge-dir", default="knowledge")
    ap.add_argument("--commit-msg-file", help="commit-msg hook arg ($1)")
    ap.add_argument("--msg-text", help="commit message text (testing)")
    ap.add_argument("--paths", nargs="*", default=None,
                    help="override staged paths (testing)")
    ap.add_argument("--trailer", default="Knowledge")
    ap.add_argument("--warn-only", action="store_true")
    ap.add_argument("--names-only", action="store_true",
                    help="v1 behaviour: accept any non-empty trailer without "
                         "verifying the named article was touched")
    ap.add_argument("--touch-window-hours", type=int, default=24,
                    help="a knowledge-repo commit to the named article within "
                         "this window counts as touched (default 24)")
    ap.add_argument("--install", action="store_true",
                    help="write .git/hooks/commit-msg in the current (product) repo")
    args = ap.parse_args(argv)

    knowledge_repo = Path(args.knowledge_repo).expanduser().resolve()
    if args.install:
        return install_hook(knowledge_repo)
    if not (knowledge_repo / args.knowledge_dir).is_dir():
        print(f"check-trailer: {knowledge_repo / args.knowledge_dir} not found",
              file=sys.stderr)
        return 1

    paths = args.paths if args.paths is not None else staged_paths()
    if not paths:
        return 0
    repo_name = Path.cwd().name

    matched = match_articles(knowledge_repo, args.knowledge_dir, repo_name, paths)
    if not matched:
        return 0

    msg = args.msg_text
    if msg is None and args.commit_msg_file:
        try:
            msg = Path(args.commit_msg_file).read_text(encoding="utf-8")
        except OSError as exc:
            print(f"check-trailer: cannot read commit message: {exc}",
                  file=sys.stderr)
            return 1
    msg = msg or ""
    # Strip comment lines (git status boilerplate) before checking.
    body = "\n".join(l for l in msg.splitlines() if not l.startswith("#"))

    trailer_re = re.compile(TRAILER_RE_TMPL.format(trailer=re.escape(args.trailer)))
    if NO_IMPACT_RE.search(body):
        return 0
    if trailer_re.search(body):
        if args.names_only:
            return 0
        return verify_touched(args, body, knowledge_repo, matched)

    print(f"⚠️  This commit touches code mapped to knowledge articles, but has "
          f"no `{args.trailer}:` trailer.")
    print("   Same-task rule: the article update belongs with this change — "
          "or at minimum, name the debt.\n")
    print("   Mapped articles:")
    for article, hits in sorted(matched.items()):
        rel = article
        try:
            rel = str(Path(article).relative_to(knowledge_repo))
        except ValueError:
            pass
        print(f"     • {rel}")
        for h in hits[:3]:
            print(f"         ← {h}")
    print(f"\n   Fix: add a trailer line to the commit message, e.g.")
    first = sorted(matched)[0]
    try:
        first = str(Path(first).relative_to(knowledge_repo))
    except ValueError:
        pass
    print(f"     {args.trailer}: {first}")
    print(f"   …or, if genuinely doc-irrelevant:")
    print(f"     no knowledge impact: <reason>")
    print(f"   Bypass (discouraged): git commit --no-verify")
    return 0 if args.warn_only else 1


if __name__ == "__main__":
    sys.exit(cli_main())
