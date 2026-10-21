"""Unit tests for site/build.py.

Run from the repository root:

    python -m unittest discover -s site

Licensed MIT. See LICENSE, part 2.
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build  # noqa: E402

FIXTURE_ENTRY = """---
title: Zebra fixture dashboard
member: Test Fixture Person
github: zz-fixture
version: 9.9.9
date: 2026-01-01
media:
  - file: 01-screen.png
    alt: A fixture screenshot of a zebra-striped grid
  - file: 02-clip.mp4
    alt: A fixture clip of a grid sorting itself
---
A fixture caption that the test looks for.
"""

FIXTURE_EMPTY_ENTRY = """---
title: Fixture with no media
member: Test Fixture Person
github: zz-fixture
version: 9.9.9
date: 2026-01-02
---
Nothing recorded yet.
"""

FIXTURE_MEMBERS = """# Members

| Number | Name | GitHub | LinkedIn | Joined | First contribution |
|---|---|---|---|---|---|
| 001 | Test Fixture Person | [zz-fixture](https://github.com/zz-fixture) | | 2026-01-01 | founder |
"""

FIXTURE_PLATFORM = """# Platform tour

The fixture platform paragraph.
"""


class BuildTest(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "repo"
        self.out = Path(self._tmp.name) / "dist"
        entry = self.root / "showcase" / "entries" / "001-zz-fixture-zebra"
        entry.mkdir(parents=True)
        (entry / "entry.md").write_text(FIXTURE_ENTRY, encoding="utf-8")
        (entry / "01-screen.png").write_bytes(b"\x89PNG\r\n\x1a\n fixture")
        (entry / "02-clip.mp4").write_bytes(b"fixture mp4")
        empty = self.root / "showcase" / "entries" / "002-zz-fixture-empty"
        empty.mkdir(parents=True)
        (empty / "entry.md").write_text(FIXTURE_EMPTY_ENTRY, encoding="utf-8")
        platform = self.root / "showcase" / "platform"
        platform.mkdir(parents=True)
        (platform / "README.md").write_text(FIXTURE_PLATFORM, encoding="utf-8")
        (self.root / "MEMBERS.md").write_text(FIXTURE_MEMBERS, encoding="utf-8")
        self.summary = build.build(self.root, self.out)

    def tearDown(self):
        self._tmp.cleanup()

    def read(self, *parts):
        path = self.out.joinpath(*parts)
        self.assertTrue(path.is_file(), f"{path} was not written")
        return path.read_text(encoding="utf-8")

    def test_every_page_carries_the_datacrafter_icon(self):
        # Without these links a browser shows a generic icon for a bookmark of the site.
        self.assertTrue((self.out / build.ICON_PNG).is_file(), "the PNG icon was not copied")
        for parts, prefix in [(("index.html",), ""), (("members.html",), ""),
                              (("entries", "001-zz-fixture-zebra.html"), "../")]:
            page = self.read(*parts)
            self.assertIn('<link rel="icon" href="data:image/svg+xml,', page)
            self.assertIn(f'<link rel="icon" type="image/png" sizes="512x512" href="{prefix}icon-512.png">', page)
            self.assertIn(f'<link rel="apple-touch-icon" href="{prefix}icon-512.png">', page)

    def test_index_lists_platform_then_entries(self):
        index = self.read("index.html")
        self.assertIn("The fixture platform paragraph.", index)
        self.assertIn("Zebra fixture dashboard", index)
        self.assertIn("Fixture with no media", index)
        self.assertLess(index.index("fixture platform"), index.index("Zebra fixture dashboard"))
        self.assertIn('alt="A fixture screenshot of a zebra-striped grid"', index)

    def test_entry_page_has_title_media_and_alt_text(self):
        page = self.read("entries", "001-zz-fixture-zebra.html")
        self.assertIn("<h1>Zebra fixture dashboard</h1>", page)
        self.assertIn("A fixture caption that the test looks for.", page)
        self.assertIn('<img src="001-zz-fixture-zebra/01-screen.png" '
                      'alt="A fixture screenshot of a zebra-striped grid"', page)
        self.assertIn('<video controls', page)
        self.assertIn('aria-label="A fixture clip of a grid sorting itself"', page)
        self.assertNotIn("media to come", page)
        self.assertTrue((self.out / "entries" / "001-zz-fixture-zebra" / "01-screen.png").is_file())
        self.assertTrue((self.out / "entries" / "001-zz-fixture-zebra" / "02-clip.mp4").is_file())

    def test_entry_without_media_says_media_to_come(self):
        page = self.read("entries", "002-zz-fixture-empty.html")
        self.assertIn("<h1>Fixture with no media</h1>", page)
        self.assertIn("Nothing recorded yet.", page)
        self.assertIn("media to come", page)

    def test_listed_but_missing_media_says_media_to_come(self):
        (self.root / "showcase" / "entries" / "001-zz-fixture-zebra" / "02-clip.mp4").unlink()
        summary = build.build(self.root, self.out)
        page = self.read("entries", "001-zz-fixture-zebra.html")
        self.assertIn("media to come", page)
        self.assertNotIn("<video", page)
        self.assertEqual(summary["to_come"], 1)

    def test_members_page_has_one_row(self):
        page = self.read("members.html")
        self.assertIn("Test Fixture Person", page)
        self.assertIn('<a href="https://github.com/zz-fixture">zz-fixture</a>', page)
        self.assertEqual(page.count("<tr>"), 2)  # header row plus one member
        self.assertIn("1 member so far", page)
        self.assertEqual(self.summary["members"], 1)

    def test_media_without_alt_text_fails_the_build(self):
        bad = FIXTURE_ENTRY.replace("    alt: A fixture clip of a grid sorting itself\n", "")
        with self.assertRaises(build.BuildError):
            build.parse_entry(bad, "fixture")

    def test_unknown_media_type_fails_the_build(self):
        bad = FIXTURE_ENTRY.replace("01-screen.png", "01-screen.gif")
        with self.assertRaises(build.BuildError):
            build.parse_entry(bad, "fixture")

    def test_refuses_to_clear_a_folder_it_did_not_make(self):
        other = Path(self._tmp.name) / "not-ours"
        other.mkdir()
        (other / "keep.txt").write_text("keep", encoding="utf-8")
        with self.assertRaises(build.BuildError):
            build.build(self.root, other)
        self.assertTrue((other / "keep.txt").is_file())

    def test_text_is_escaped(self):
        tricky = FIXTURE_EMPTY_ENTRY.replace("Nothing recorded yet.", "<script>x</script>")
        (self.root / "showcase" / "entries" / "002-zz-fixture-empty" / "entry.md").write_text(
            tricky, encoding="utf-8")
        build.build(self.root, self.out)
        page = self.read("entries", "002-zz-fixture-empty.html")
        self.assertNotIn("<script>", page)
        self.assertIn("&lt;script&gt;", page)


class RepositoryBuildTest(unittest.TestCase):
    """The real repository content builds, into a temporary folder."""

    def test_repository_builds(self):
        root = Path(__file__).resolve().parent.parent
        with tempfile.TemporaryDirectory() as tmp:
            summary = build.build(root, Path(tmp) / "dist")
            self.assertGreaterEqual(summary["entries"], 1)
            self.assertGreaterEqual(summary["members"], 1)


if __name__ == "__main__":
    unittest.main()
