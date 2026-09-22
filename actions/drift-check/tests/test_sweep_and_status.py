"""sweep-report --size rows and the kb-status screen (smoke)."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import kb_status  # noqa: E402
import sweep_report  # noqa: E402


def art(words: int, facts: bool, lb: bool = False) -> str:
    fm = "---\nupdated: 2026-01-01\narea: a\n" + ("load_bearing: true\n" if lb else "") + "---\n"
    body = "# T\n\n" + ("word " * words) + "\n" + ("\n## Facts\n\n- a fact\n" if facts else "")
    return fm + body


class SizeAndStatusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.k = Path(self.tmp.name) / "knowledge"
        (self.k / "concepts" / "a").mkdir(parents=True)
        (self.k / "log" / "entries").mkdir(parents=True)
        (self.k / "concepts/a/big.md").write_text(art(4500, False, lb=True), encoding="utf-8")
        (self.k / "concepts/a/small.md").write_text(art(100, True), encoding="utf-8")
        (self.k / "scopes.md").write_text("- **concepts** — c\n- **concepts/a** — scope\n", encoding="utf-8")
        (self.k / "log/entries/2026-01-02-x.md").write_text("## 2026-01-02 — X\n\n- b\n", encoding="utf-8")

    def test_size_rows_largest_first_with_flags(self) -> None:
        rows = sweep_report.size_rows(str(self.k))
        self.assertEqual([Path(r["path"]).name for r in rows], ["big.md", "small.md"])
        self.assertGreater(rows[0]["words"], sweep_report.SIZE_WORDS)
        self.assertEqual((rows[0]["facts"], rows[0]["load_bearing"]), (False, True))
        self.assertEqual((rows[1]["facts"], rows[1]["load_bearing"]), (True, False))
        self.assertIsNone(rows[0]["facts_pos"])
        self.assertGreater(rows[1]["facts_pos"], sweep_report.FACTS_LATE)   # Facts at the end of small.md

    def test_kb_status_smoke(self) -> None:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = kb_status.cli_main(["--knowledge-dir", str(self.k)])
        out = buf.getvalue()
        self.assertEqual(rc, 0)
        self.assertIn("2 articles in 1 areas", out)
        self.assertIn("1 articles over 4000 words, 1 without ## Facts, 1 with Facts in the bottom half", out)
        self.assertIn("2026-01-02 — X", out)
        self.assertLess(out.count("\n"), 30)


if __name__ == "__main__":
    unittest.main()
