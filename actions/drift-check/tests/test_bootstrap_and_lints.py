"""bootstrap check/install (temp repos), sweep --plain-terms rows, roll-log long-entry
warning, provenance code-cite liveness."""
from __future__ import annotations

import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import bootstrap  # noqa: E402
import kb_paths  # noqa: E402
import provenance_report  # noqa: E402
import roll_log  # noqa: E402
import sweep_report  # noqa: E402


class BootstrapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        t = Path(self.tmp.name)
        self.kb = t / "kb"; (self.kb / "scripts").mkdir(parents=True)
        (self.kb / ".claude/skills/kb").mkdir(parents=True)
        (self.kb / ".claude/skills/kb/SKILL.md").write_text("---\nname: kb\n---\n", encoding="utf-8")
        (self.kb / "scripts/check-trailer").write_text("#!/bin/sh\n", encoding="utf-8")
        self.prod = t / "Prod"; self.prod.mkdir()
        for r in (self.kb, self.prod):
            subprocess.run(["git", "-C", str(r), "init", "-q"], check=True)
        self.home = t / "home"; self.home.mkdir()
        self._orig = kb_paths.knowledge_repo
        kb_paths.knowledge_repo = lambda: self.kb          # skill_dir() resolves against the test kb
        self.addCleanup(setattr, kb_paths, "knowledge_repo", self._orig)

    def test_check_reports_everything_missing_then_install_fixes(self) -> None:
        missing = bootstrap.check(self.kb, [self.prod], self.home)
        self.assertEqual(len(missing), 4)
        with contextlib.redirect_stdout(io.StringIO()):
            rc = bootstrap.install(self.kb, [self.prod], self.home)
        self.assertEqual(rc, 0)
        self.assertEqual(bootstrap.check(self.kb, [self.prod], self.home), [])
        self.assertIn("check-trailer", (self.prod / ".git/hooks/commit-msg").read_text())
        self.assertIn("kb-status", (self.prod / ".claude/settings.local.json").read_text())
        self.assertTrue((self.home / ".claude/skills/kb").is_symlink())
        # idempotent and preserves existing settings
        (self.prod / ".claude/settings.local.json").write_text(
            '{"permissions": {"allow": ["Bash(ls:*)"]}}\n', encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(bootstrap.install(self.kb, [self.prod], self.home), 0)
        cfg = (self.prod / ".claude/settings.local.json").read_text()
        self.assertIn("Bash(ls:*)", cfg); self.assertIn("kb-status", cfg)


class LintTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.k = Path(self.tmp.name) / "knowledge"
        (self.k / "concepts/a").mkdir(parents=True)
        (self.k / "log/entries").mkdir(parents=True)
        fm = "---\nupdated: 2026-01-01\narea: a\n---\n# T\n\n"
        (self.k / "concepts/a/inc.md").write_text(fm + "seen *(field: Q 2026-07-20)* and *(field: B)*\n", encoding="utf-8")
        (self.k / "concepts/a/done.md").write_text(fm + "seen *(field: Q)*\n\n## In plain terms\n\n- ok\n", encoding="utf-8")
        (self.k / "concepts/a/code.md").write_text(
            fm + "x *(code: `Ledger.m:12`)* y *(reported: v; code: Sources/Foo/Bar.swift:3)* z *(code: Gone.m:1)*\n", encoding="utf-8")
        self.src = Path(self.tmp.name) / "src"; (self.src / "Sources/Foo").mkdir(parents=True)
        (self.src / "Ledger.m").write_text("", encoding="utf-8"); (self.src / "Sources/Foo/Bar.swift").write_text("", encoding="utf-8")

    def test_plain_terms_candidates(self) -> None:
        rows = sweep_report.plain_terms_rows(str(self.k))
        self.assertEqual([(Path(r["path"]).name, r["field_tags"]) for r in rows], [("inc.md", 2)])

    def test_roll_log_check_warns_on_long_entry(self) -> None:
        (self.k / "log/entries/2026-01-02-long.md").write_text("## 2026-01-02 — L\n\n" + "word " * 450 + "\n", encoding="utf-8")
        (self.k / "log/entries/2026-01-03-short.md").write_text("## 2026-01-03 — S\n\n- fine\n", encoding="utf-8")
        self.assertEqual([n for n, _ in roll_log.long_entries(self.k)], ["2026-01-02-long.md"])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(roll_log.cli_main(["--knowledge-dir", str(self.k), "--check"]), 0)
        self.assertNotIn("words", buf.getvalue())                       # --check stays quiet about length

    def test_code_cite_liveness(self) -> None:
        res = provenance_report.liveness(str(self.k), [str(self.src)])
        self.assertEqual((res["total"], res["live"]), (3, 2))
        self.assertEqual(res["dead"][0][2], "Gone.m")


if __name__ == "__main__":
    unittest.main()
