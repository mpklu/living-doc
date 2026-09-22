"""build-index: one _index.md per content directory (recursive), scope lines by
path, decisions column, H1 fallback, missing-scope failure, orphan removal."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import build_index  # noqa: E402


def cli(*args: str) -> int:
    with contextlib.redirect_stdout(io.StringIO()):
        return build_index.cli_main(list(args))


def write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def article(h1: str, status: str = "thin→growing — first pass", facts: bool = False,
            decisions: int = 0, affects=("Src/**/A.swift", "Src/B.m", "**/EDI/**")) -> str:
    fm = ["---", "updated: 2026-05-01", "area: x", f"status: {status}", "affects:"]
    fm += [f'  - "{a}"' for a in affects] + ["---"]
    body = f"\n# {h1}\n\nprose\n"
    if decisions:
        body += "\n## Decisions\n\n" + "".join(f"- 2026-09-0{i+1} — chose X{i} *(decision: K)*\n" for i in range(decisions))
    if facts:
        body += "\n## Facts\n\n- a fact\n"
    return "\n".join(fm) + body


SCOPES = """# Scopes

- **concepts** — reference articles by area
- **concepts/a** — area A scope
- **concepts/b** — area B scope
- **concepts/b/nested** — deeper B
- **connections** — cross-cutting
"""


class BuildIndexTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.k = Path(self.tmp.name) / "knowledge"
        write(self.k / "concepts/a/one.md", article("One", decisions=2))
        write(self.k / "concepts/b/nested/two.md", article("Two, from its H1", facts=True))
        write(self.k / "connections/three.md", article("Three", status="deprecated"))
        write(self.k / "scopes.md", SCOPES)

    def test_one_index_per_content_dir_recursive(self) -> None:
        files, missing = build_index.generate(self.k)
        self.assertEqual(missing, [])
        rels = sorted(p.relative_to(self.k).as_posix() for p in files)
        self.assertEqual(rels, ["_index.md", "concepts/_index.md", "concepts/a/_index.md",
                                "concepts/b/_index.md", "concepts/b/nested/_index.md", "connections/_index.md"])
        root = files[self.k / "_index.md"]
        self.assertIn("| [concepts/](concepts/_index.md) | 2 | 1 | 2 | reference articles by area |", root)
        self.assertIn("| [connections/](connections/_index.md) | 1 | 0 | 0 | cross-cutting |", root)
        b = files[self.k / "concepts/b/_index.md"]
        self.assertIn("# concepts/b\n\narea B scope\n", b)
        self.assertIn("| [nested/](nested/_index.md) | 1 | 1 | 0 | deeper B |", b)
        self.assertNotIn("| concepts/b/nested/two.md", b)
        leaf = files[self.k / "concepts/b/nested/_index.md"]
        self.assertIn("| concepts/b/nested/two.md | Two, from its H1 | thin→growing | 2026-05-01 | F |  | A.swift, B.m, +1 |", leaf)
        self.assertIn("| concepts/a/one.md | One | thin→growing | 2026-05-01 |  | D2 |", files[self.k / "concepts/a/_index.md"])
        self.assertIn("*(deprecated)* Three", files[self.k / "connections/_index.md"])

    def test_missing_scope_fails_check_only(self) -> None:
        write(self.k / "concepts/zed/z.md", article("Z"))
        _, missing = build_index.generate(self.k)
        self.assertEqual(missing, ["concepts/zed"])
        self.assertEqual(cli("--knowledge-dir", str(self.k)), 0)
        self.assertEqual(cli("--knowledge-dir", str(self.k), "--check"), 1)

    def test_cli_writes_checks_and_removes_orphans(self) -> None:
        self.assertEqual(cli("--knowledge-dir", str(self.k)), 0)
        self.assertTrue((self.k / "concepts/a/_index.md").is_file())
        self.assertEqual(cli("--knowledge-dir", str(self.k), "--check"), 0)
        write(self.k / "concepts/gone/_index.md", "old\n")
        self.assertEqual(cli("--knowledge-dir", str(self.k), "--check"), 1)
        self.assertEqual(cli("--knowledge-dir", str(self.k)), 0)
        self.assertFalse((self.k / "concepts/gone/_index.md").exists())
        self.assertNotIn(self.k / "concepts/a/_index.md", build_index.all_articles(self.k))


if __name__ == "__main__":
    unittest.main()
