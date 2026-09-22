"""check-trailer: the `Knowledge:` trailer must name an article that was
actually touched (dirty in the KB working tree, committed recently, or
`updated:` today) — not merely a plausible-looking path."""
from __future__ import annotations

import contextlib
import datetime as dt
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import check_trailer  # noqa: E402


def git(repo: Path, *args: str, env: dict | None = None) -> str:
    e = {**os.environ, **(env or {})}
    e.setdefault("GIT_AUTHOR_NAME", "t"); e.setdefault("GIT_AUTHOR_EMAIL", "t@t")
    e.setdefault("GIT_COMMITTER_NAME", "t"); e.setdefault("GIT_COMMITTER_EMAIL", "t@t")
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True, env=e).stdout


ARTICLE = """---
updated: 2026-01-01
area: demo
affects:
  - "Source/**"
---

# Demo article
"""


class CheckTrailerTouchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.kb = root / "kb"
        (self.kb / "knowledge" / "concepts" / "demo").mkdir(parents=True)
        (self.kb / "scripts").mkdir()
        self.article = self.kb / "knowledge" / "concepts" / "demo" / "thing.md"
        self.article.write_text(ARTICLE, encoding="utf-8")
        git(self.kb, "init", "-q")
        git(self.kb, "add", "-A")
        old = "2020-01-01T00:00:00"
        git(self.kb, "commit", "-q", "-m", "seed",
            env={"GIT_AUTHOR_DATE": old, "GIT_COMMITTER_DATE": old})
        self.product = root / "ProductRepo"
        self.product.mkdir()
        self.cwd = os.getcwd()
        os.chdir(self.product)

    def tearDown(self) -> None:
        os.chdir(self.cwd)
        self.tmp.cleanup()

    def run_check(self, msg: str, *extra: str) -> int:
        with contextlib.redirect_stdout(io.StringIO()):
            return self._run(msg, *extra)

    def _run(self, msg: str, *extra: str) -> int:
        return check_trailer.cli_main([
            "--knowledge-repo", str(self.kb), "--paths", "Source/Foo.m",
            "--msg-text", msg, *extra,
        ])

    def test_no_trailer_blocks(self) -> None:
        self.assertEqual(self.run_check("fix thing"), 1)

    def test_no_impact_line_passes(self) -> None:
        self.assertEqual(self.run_check("fix\n\nno knowledge impact: typo"), 0)

    def test_named_article_clean_and_old_blocks(self) -> None:
        self.assertEqual(self.run_check("fix\n\nKnowledge: concepts/demo/thing.md"), 1)

    def test_named_article_dirty_passes(self) -> None:
        self.article.write_text(ARTICLE + "\nmore\n", encoding="utf-8")
        self.assertEqual(self.run_check("fix\n\nKnowledge: concepts/demo/thing.md"), 0)

    def test_named_article_recent_commit_passes(self) -> None:
        self.article.write_text(ARTICLE + "\nmore\n", encoding="utf-8")
        git(self.kb, "commit", "-q", "-am", "touch")
        self.assertEqual(self.run_check("fix\n\nKnowledge: concepts/demo/thing.md"), 0)

    def test_updated_today_passes(self) -> None:
        today = dt.date.today().isoformat()
        self.article.write_text(ARTICLE.replace("2026-01-01", today), encoding="utf-8")
        git(self.kb, "commit", "-q", "-am", "bump",
            env={"GIT_AUTHOR_DATE": "2020-01-02T00:00:00",
                 "GIT_COMMITTER_DATE": "2020-01-02T00:00:00"})
        self.assertEqual(self.run_check("fix\n\nKnowledge: concepts/demo/thing.md"), 0)

    def test_nonexistent_article_blocks(self) -> None:
        self.assertEqual(self.run_check("fix\n\nKnowledge: concepts/demo/nope.md"), 1)

    def test_free_text_trailer_blocks(self) -> None:
        self.assertEqual(self.run_check("fix\n\nKnowledge: will do later"), 1)

    def test_trailer_path_variants_resolve(self) -> None:
        self.article.write_text(ARTICLE + "\nmore\n", encoding="utf-8")
        for v in ("knowledge/concepts/demo/thing.md", "`concepts/demo/thing.md`",
                  "concepts/demo/thing.md, and notes"):
            self.assertEqual(self.run_check(f"fix\n\nKnowledge: {v}"), 0, v)

    def test_names_only_restores_v1(self) -> None:
        self.assertEqual(self.run_check("fix\n\nKnowledge: concepts/demo/thing.md",
                                        "--names-only"), 0)

    def test_warn_only_never_blocks(self) -> None:
        self.assertEqual(self.run_check("fix\n\nKnowledge: concepts/demo/thing.md",
                                        "--warn-only"), 0)


if __name__ == "__main__":
    unittest.main()
