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

Deliberately helpful, not hostile: any non-empty trailer satisfies (v1
doesn't police that it names the right article — the printed list is
guidance), `--warn-only` never blocks, and `git commit --no-verify`
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
NO_IMPACT_RE = re.compile(r"(?i)no knowledge impact\s*:")


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

    # external: entries — repo-level mapping by name.
    if paths:
        for article in sorted(kdir.rglob("*.md")):
            fm = parse_frontmatter(article)
            if not fm:
                continue
            for entry in fm.get("affects", []) or []:
                if (
                    isinstance(entry, str)
                    and entry.startswith("external:")
                    and repo_name.lower() in entry.lower()
                ):
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
    if trailer_re.search(body) or NO_IMPACT_RE.search(body):
        return 0

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
