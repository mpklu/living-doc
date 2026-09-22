"""roll-log: entry files validate; old ones move into log/YYYY-MM/ untouched."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import roll_log  # noqa: E402


def quiet(fn, *args):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(*args)


class RollLogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.k = Path(self.tmp.name) / "knowledge"
        self.e = self.k / "log" / "entries"
        self.e.mkdir(parents=True)
        for d, slug in [("2026-05-10", "a"), ("2026-06-05", "b"), ("2026-06-22", "c")]:
            (self.e / f"{d}-{slug}.md").write_text(f"## {d} — {slug}\n\n- body {slug}\n", encoding="utf-8")

    def test_load_entries_newest_first(self) -> None:
        names = [n for _, n, _ in roll_log.load_entries(self.k)]
        self.assertEqual(names, ["2026-06-22-c.md", "2026-06-05-b.md", "2026-05-10-a.md"])

    def test_bad_header_or_name_fails(self) -> None:
        (self.e / "2026-06-30-bad.md").write_text("no header\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            roll_log.load_entries(self.k)
        (self.e / "2026-06-30-bad.md").write_text("## 2026-07-01 — mismatch\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            roll_log.load_entries(self.k)
        (self.e / "2026-06-30-bad.md").unlink()
        self.assertEqual(quiet(roll_log.cli_main, ["--knowledge-dir", str(self.k), "--check"]), 0)

    def test_roll_moves_old_files_verbatim(self) -> None:
        before = (self.e / "2026-05-10-a.md").read_text(encoding="utf-8")
        self.assertEqual(quiet(roll_log.roll, self.k, "2026-06-20", False), 0)
        self.assertEqual(sorted(p.name for p in self.e.glob("*.md")), ["2026-06-22-c.md"])
        self.assertEqual((self.k / "log/2026-05/2026-05-10-a.md").read_text(encoding="utf-8"), before)
        self.assertTrue((self.k / "log/2026-06/2026-06-05-b.md").is_file())
        self.assertEqual(quiet(roll_log.roll, self.k, "2026-06-20", False), 0)     # idempotent

    def test_dry_run_moves_nothing(self) -> None:
        self.assertEqual(quiet(roll_log.roll, self.k, "2026-06-20", True), 0)
        self.assertEqual(len(list(self.e.glob("*.md"))), 3)
        self.assertFalse((self.k / "log/2026-05").exists())


if __name__ == "__main__":
    unittest.main()
