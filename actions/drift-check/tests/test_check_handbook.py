"""check-handbook: a current-state page must not fall behind the concept articles it cites."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import check_handbook  # noqa: E402


def article(updated: str) -> str:
    return f"---\nupdated: {updated}\narea: a\n---\n\n# Source\n"


def page(updated: str, sources: list[str] | None) -> str:
    fm = f"---\nupdated: {updated}\narea: handbook\n"
    if sources is not None:
        fm += "sources:\n" + "".join(f"  - {s}\n" for s in sources)
    return fm + "---\n\n# Page\n"


class CheckHandbookTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.k = Path(self.tmp.name) / "knowledge"
        (self.k / "concepts" / "a").mkdir(parents=True)
        (self.k / "handbook").mkdir(parents=True)
        (self.k / "concepts/a/src.md").write_text(article("2026-11-01"), encoding="utf-8")

    def write_page(self, text: str, name: str = "p.md") -> None:
        (self.k / "handbook" / name).write_text(text, encoding="utf-8")

    def codes(self) -> list[str]:
        return [f["code"] for f in check_handbook.check(self.k)]

    def test_fresh_page_has_no_findings(self) -> None:
        self.write_page(page("2026-11-01", ["concepts/a/src.md"]))
        self.assertEqual(self.codes(), [])

    def test_source_updated_after_page_is_stale(self) -> None:
        self.write_page(page("2026-10-01", ["concepts/a/src.md"]))
        self.assertEqual(self.codes(), ["stale"])

    def test_missing_sources_is_an_error(self) -> None:
        self.write_page(page("2026-11-01", None))
        self.assertEqual(self.codes(), ["no-sources"])

    def test_source_naming_no_file_is_an_error(self) -> None:
        self.write_page(page("2026-11-01", ["concepts/a/gone.md"]))
        self.assertEqual(self.codes(), ["dead-source"])

    def test_index_files_are_not_pages(self) -> None:
        (self.k / "handbook" / "_index.md").write_text("# handbook\n", encoding="utf-8")
        self.assertEqual(check_handbook.pages(self.k), [])

    def test_no_handbook_dir_is_fine(self) -> None:
        (self.k / "handbook").rmdir()
        self.assertEqual(check_handbook.check(self.k), [])

    def test_stale_warns_but_exits_0_unless_strict(self) -> None:
        self.write_page(page("2026-10-01", ["concepts/a/src.md"]))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(check_handbook.cli_main(["--knowledge-dir", str(self.k)]), 0)
            self.assertEqual(check_handbook.cli_main(["--knowledge-dir", str(self.k), "--strict"]), 1)

    def test_errors_exit_1(self) -> None:
        self.write_page(page("2026-11-01", ["concepts/a/gone.md"]))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(check_handbook.cli_main(["--knowledge-dir", str(self.k)]), 1)


if __name__ == "__main__":
    unittest.main()
