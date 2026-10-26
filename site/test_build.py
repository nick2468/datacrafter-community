"""Unit tests for site/build.py.

Run from the repository root:

    python -m unittest discover -s site

Licensed MIT. See LICENSE, part 2.
"""

import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build  # noqa: E402

FIXTURE_ENTRY = """---
title: Zebra fixture dashboard
summary: A fixture summary for the zebra card.
member: Test Fixture Person
github: zz-fixture
version: 9.9.9
date: 2026-01-01
moved_from: 001-zz-fixture-old-zebra
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
Nothing recorded yet. This second sentence stays off the card.
"""

FIXTURE_OTHER_ENTRY = """---
title: Gadget fixture report
member: Second Fixture Person
github: zz-other
version: 9.9.9
date: 2026-01-03
---
A gadget fixture caption.
"""

FIXTURE_OFFICIAL_ENTRY = """---
title: Fixture official tour
summary: A fixture tour of the screens.
author: DataCrafter
version: 9.9.9
date: 2026-01-04
media:
  - file: 01-home.png
    alt: A fixture screenshot of the home screen
---
An official fixture caption.
"""

FIXTURE_MEMBERS = """# Members

| Number | Name | GitHub | LinkedIn | Joined | First contribution |
|---|---|---|---|---|---|
| 001 | Test Fixture Person | [zz-fixture](https://github.com/zz-fixture) | | 2026-01-01 | founder |
| 002 | Second Fixture Person | [zz-other](https://github.com/zz-other) | | 2026-01-02 | showcase entry |
| 003 | Quiet Fixture Person | [zz-quiet](https://github.com/zz-quiet) | | 2026-01-03 | bug report |
"""

ZEBRA = "001-zz-fixture-zebra"
EMPTY = "002-zz-fixture-empty"
OTHER = "003-zz-other-gadget"
OFFICIAL = "000-datacrafter-tour"

CARD = re.compile(r'<li class="card">(.*?)</li>', re.S)


def media_entry(count):
    """FIXTURE_EMPTY_ENTRY with count screenshots in its media list."""
    items = "".join(f"  - file: {n:02}-screen.png\n    alt: Fixture screenshot {n}\n"
                    for n in range(1, count + 1))
    return FIXTURE_EMPTY_ENTRY.replace("date: 2026-01-02\n", f"date: 2026-01-02\nmedia:\n{items}")


def section(page, heading_id):
    """The HTML of the <section> labelled by heading_id."""
    match = re.search(rf'<section aria-labelledby="{heading_id}">(.*?)</section>', page, re.S)
    assert match, f"no section labelled {heading_id}"
    return match.group(1)


def card_links(fragment):
    """The (href, title) of each card's link, in order."""
    return re.findall(r'<a class="card-link" href="([^"]+)">([^<]+)</a>', fragment)


class BuildTest(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "repo"
        self.out = Path(self._tmp.name) / "dist"
        self.add_entry(ZEBRA, FIXTURE_ENTRY, {"01-screen.png": b"\x89PNG\r\n\x1a\n fixture",
                                              "02-clip.mp4": b"fixture mp4"})
        self.add_entry(EMPTY, FIXTURE_EMPTY_ENTRY)
        self.add_entry(OTHER, FIXTURE_OTHER_ENTRY)
        self.add_entry(OFFICIAL, FIXTURE_OFFICIAL_ENTRY, {"01-home.png": b"\x89PNG\r\n\x1a\n home"})
        (self.root / "MEMBERS.md").write_text(FIXTURE_MEMBERS, encoding="utf-8")
        self.summary = build.build(self.root, self.out)

    def tearDown(self):
        self._tmp.cleanup()

    def add_entry(self, slug, text, files=None):
        folder = self.root / "showcase" / "entries" / slug
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "entry.md").write_text(text, encoding="utf-8")
        for name, data in (files or {}).items():
            (folder / name).write_bytes(data)
        return folder

    def read(self, *parts):
        path = self.out.joinpath(*parts)
        self.assertTrue(path.is_file(), f"{path} was not written")
        return path.read_text(encoding="utf-8")

    def test_every_page_carries_the_datacrafter_icon(self):
        # Without these links a browser shows a generic icon for a bookmark of the site.
        self.assertTrue((self.out / build.ICON_PNG).is_file(), "the PNG icon was not copied")
        for parts, prefix in [(("index.html",), ""), (("members.html",), ""),
                              (("entries", f"{ZEBRA}.html"), "../"),
                              (("entries", "001-zz-fixture-old-zebra.html"), "../")]:
            page = self.read(*parts)
            self.assertIn('<link rel="icon" href="data:image/svg+xml,', page)
            self.assertIn(f'<link rel="icon" type="image/png" sizes="512x512" href="{prefix}icon-512.png">', page)
            self.assertIn(f'<link rel="apple-touch-icon" href="{prefix}icon-512.png">', page)

    def test_every_page_links_back_to_datacrafter_net(self):
        pages = sorted(self.out.rglob("*.html"))
        self.assertEqual(len(pages), 2 + 4 + 1)  # index and members, four showcases, one redirect
        for path in pages:
            page = path.read_text(encoding="utf-8")
            nav = page.split('<nav aria-label="Site">')[1].split("</nav>")[0]
            footer = page.split("<footer>")[1].split("</footer>")[0]
            for part in (nav, footer):
                self.assertIn('<a href="https://www.datacrafter.net">', part, path.name)
            # Our own site, so it opens in the same tab.
            self.assertNotIn("target=", page, path.name)

    def test_header_and_footer_community_links_go_to_our_community_page(self):
        for path in sorted(self.out.rglob("*.html")):
            page = path.read_text(encoding="utf-8")
            nav = page.split('<nav aria-label="Site">')[1].split("</nav>")[0]
            self.assertIn('<a href="https://www.datacrafter.net/community">Community</a>', nav, path.name)
            self.assertNotIn("github.com", nav, path.name)
            footer = page.split("<footer>")[1].split("</footer>")[0]
            self.assertIn('<a href="https://www.datacrafter.net/community">Help shape what comes next.</a>', footer, path.name)
            self.assertNotIn("github.com", footer, path.name)

    def test_header_is_the_brand_and_three_links(self):
        # The brand, with the mark, goes home to www.datacrafter.net. The header has no
        # link to the showcase index: entry and members pages link back from their bodies.
        for path in sorted(self.out.rglob("*.html")):
            page = path.read_text(encoding="utf-8")
            header = page.split("<header>")[1].split("</header>")[0]
            brand = header.split('<a class="brand" ')[1].split("</a>")[0]
            self.assertTrue(brand.startswith('href="https://www.datacrafter.net"><svg '), path.name)
            self.assertTrue(brand.endswith("</svg>DataCrafter"), path.name)
            nav = header.split('<nav aria-label="Site">')[1].split("</nav>")[0]
            labels = re.findall(r">([^<>]+)</a>", nav)
            self.assertEqual(labels, ["DataCrafter.net", "Members", "Community"], path.name)
            self.assertNotIn("index.html", header, path.name)

    def test_members_page_links_back_to_the_showcase(self):
        page = self.read("members.html")
        self.assertIn('<a href="index.html">Back to the showcase</a>', page)

    def test_footer_states_the_contribution_terms_not_cc_by(self):
        # Founder 2026-10-22: contributions are licensed to DataCrafter Software Labs alone.
        for path in sorted(self.out.rglob("*.html")):
            page = path.read_text(encoding="utf-8")
            self.assertNotIn("CC BY", page, path.name)
            footer = page.split("<footer>")[1].split("</footer>")[0]
            self.assertIn("shown with their makers' permission and credited to them", footer, path.name)

    def test_index_leads_with_a_card_for_every_showcase(self):
        grid = section(self.read("index.html"), "showcases")
        links = card_links(grid)
        self.assertEqual(links, [
            (f"entries/{OFFICIAL}.html", "Fixture official tour"),
            (f"entries/{ZEBRA}.html", "Zebra fixture dashboard"),
            (f"entries/{EMPTY}.html", "Fixture with no media"),
            (f"entries/{OTHER}.html", "Gadget fixture report"),
        ])

    def test_each_card_is_one_link_named_by_its_title(self):
        index = self.read("index.html")
        cards = CARD.findall(index)
        self.assertEqual(len(cards), 4 + 3)  # the top grid, then the member groups
        for card in cards:
            # One link, and its only text is the title, so the title is its accessible name.
            self.assertEqual(card.count("<a "), 1, card)
            self.assertEqual(len(card_links(card)), 1, card)
            self.assertIn('<p class="byline">By ', card)

    def test_card_shows_cover_summary_and_author(self):
        grid = section(self.read("index.html"), "showcases")
        zebra = next(c for c in CARD.findall(grid) if ZEBRA in c)
        self.assertIn(f'<img class="cover" src="entries/{ZEBRA}/01-screen.png" alt=""', zebra)
        self.assertIn("A fixture summary for the zebra card.", zebra)
        self.assertIn("By Test Fixture Person", zebra)

    def test_card_without_summary_uses_the_first_sentence(self):
        grid = section(self.read("index.html"), "showcases")
        empty = next(c for c in CARD.findall(grid) if EMPTY in c)
        self.assertIn('<p class="summary">Nothing recorded yet.</p>', empty)
        self.assertNotIn("second sentence", empty)
        self.assertIn("media to come", empty)

    def test_index_shows_no_screenshots_inline(self):
        index = self.read("index.html")
        self.assertNotIn("<figure", index)
        self.assertNotIn("<video", index)
        self.assertNotIn("A fixture screenshot of a zebra-striped grid", index)

    def test_one_page_per_showcase(self):
        for slug, title in [(OFFICIAL, "Fixture official tour"), (ZEBRA, "Zebra fixture dashboard"),
                            (EMPTY, "Fixture with no media"), (OTHER, "Gadget fixture report")]:
            page = self.read("entries", f"{slug}.html")
            self.assertIn(f"<h1>{title}</h1>", page)
            self.assertIn('<a href="../index.html">Back to the showcase</a>', page)
        self.assertEqual(self.summary["entries"], 4)

    def test_members_section_groups_cards_by_member_in_ledger_order(self):
        members = section(self.read("index.html"), "by-member")
        groups = re.findall(r'<div class="member">\s*<h3>([^<]+)</h3>(.*?)</ul>\s*</div>',
                            members, re.S)
        self.assertEqual([name for name, _ in groups],
                         ["Test Fixture Person", "Second Fixture Person"])
        self.assertEqual(card_links(groups[0][1]), [
            (f"entries/{ZEBRA}.html", "Zebra fixture dashboard"),
            (f"entries/{EMPTY}.html", "Fixture with no media"),
        ])
        self.assertEqual(card_links(groups[1][1]), [(f"entries/{OTHER}.html", "Gadget fixture report")])
        self.assertIn('Data Crafter 001 | <a href="https://github.com/zz-fixture">@zz-fixture</a>',
                      groups[0][1])
        # A member with no showcase has no group.
        self.assertNotIn("Quiet Fixture Person", members)
        # Card titles sit one level below the member's name.
        self.assertIn(f'<h4><a class="card-link" href="entries/{OTHER}.html">', members)

    def test_official_showcase_is_in_the_top_grid_only(self):
        index = self.read("index.html")
        self.assertIn(f"entries/{OFFICIAL}.html", section(index, "showcases"))
        self.assertNotIn(OFFICIAL, section(index, "by-member"))
        self.assertNotIn("DataCrafter Software Labs", section(index, "by-member"))
        self.assertIn("By DataCrafter Software Labs", section(index, "showcases"))
        self.assertEqual(self.summary["official"], 1)

    def test_official_showcase_page_credits_datacrafter(self):
        page = self.read("entries", f"{OFFICIAL}.html")
        self.assertIn('<p class="eyebrow">Official showcase</p>', page)
        self.assertIn('<p class="meta">DataCrafter Software Labs | DataCrafter 9.9.9', page)
        self.assertNotIn("github.com/", page.split("<main")[1].split("</main>")[0])
        member_page = self.read("entries", f"{ZEBRA}.html")
        self.assertIn('<p class="eyebrow">Member showcase</p>', member_page)

    def test_official_showcase_leads_the_grid_whatever_its_number(self):
        (self.root / "showcase" / "entries" / OFFICIAL).rename(
            self.root / "showcase" / "entries" / "009-datacrafter-tour")
        build.build(self.root, self.out)
        links = card_links(section(self.read("index.html"), "showcases"))
        self.assertEqual(links[0], ("entries/009-datacrafter-tour.html", "Fixture official tour"))

    def test_old_address_redirects_to_the_new_page(self):
        page = self.read("entries", "001-zz-fixture-old-zebra.html")
        self.assertIn(f'<meta http-equiv="refresh" content="0; url={ZEBRA}.html">', page)
        self.assertIn(f'<link rel="canonical" href="{ZEBRA}.html">', page)
        self.assertIn(f'<a href="{ZEBRA}.html">', page)
        self.assertEqual(self.summary["redirects"], 1)

    def test_moved_from_a_live_folder_fails_the_build(self):
        clash = FIXTURE_OTHER_ENTRY.replace("date: 2026-01-03\n",
                                            f"date: 2026-01-03\nmoved_from: {EMPTY}\n")
        self.add_entry(OTHER, clash)
        with self.assertRaises(build.BuildError):
            build.build(self.root, self.out)

    def test_moved_from_claimed_twice_fails_the_build(self):
        twice = FIXTURE_OTHER_ENTRY.replace("date: 2026-01-03\n",
                                            "date: 2026-01-03\nmoved_from: 001-zz-fixture-old-zebra\n")
        self.add_entry(OTHER, twice)
        with self.assertRaises(build.BuildError):
            build.build(self.root, self.out)

    def test_showcase_whose_member_is_not_in_the_ledger_still_gets_a_group(self):
        stray = FIXTURE_OTHER_ENTRY.replace("Second Fixture Person", "Stray Fixture Person") \
                                   .replace("zz-other", "zz-stray")
        self.add_entry("004-zz-stray-thing", stray)
        build.build(self.root, self.out)
        members = section(self.read("index.html"), "by-member")
        self.assertIn("<h3>Stray Fixture Person</h3>", members)
        self.assertLess(members.index("Second Fixture Person"), members.index("Stray Fixture Person"))

    def test_entry_page_has_title_media_and_alt_text(self):
        page = self.read("entries", f"{ZEBRA}.html")
        self.assertIn("<h1>Zebra fixture dashboard</h1>", page)
        self.assertIn("A fixture caption that the test looks for.", page)
        self.assertIn(f'<img src="{ZEBRA}/01-screen.png" '
                      'alt="A fixture screenshot of a zebra-striped grid"', page)
        self.assertIn('<video controls', page)
        self.assertIn('aria-label="A fixture clip of a grid sorting itself"', page)
        self.assertNotIn("media to come", page)
        self.assertTrue((self.out / "entries" / ZEBRA / "01-screen.png").is_file())
        self.assertTrue((self.out / "entries" / ZEBRA / "02-clip.mp4").is_file())

    def test_entry_without_media_says_media_to_come(self):
        page = self.read("entries", f"{EMPTY}.html")
        self.assertIn("<h1>Fixture with no media</h1>", page)
        self.assertIn("Nothing recorded yet.", page)
        self.assertIn("media to come", page)

    def test_listed_but_missing_media_says_media_to_come(self):
        (self.root / "showcase" / "entries" / ZEBRA / "02-clip.mp4").unlink()
        summary = build.build(self.root, self.out)
        page = self.read("entries", f"{ZEBRA}.html")
        self.assertIn("media to come", page)
        self.assertNotIn("<video", page)
        self.assertEqual(summary["to_come"], 1)

    def test_members_page_has_the_ledger(self):
        page = self.read("members.html")
        self.assertIn("Test Fixture Person", page)
        self.assertIn('<a href="https://github.com/zz-fixture">zz-fixture</a>', page)
        self.assertEqual(page.count("<tr>"), 4)  # header row plus three members
        self.assertIn("3 members so far", page)
        self.assertEqual(self.summary["members"], 3)

    def test_media_without_alt_text_fails_the_build(self):
        bad = FIXTURE_ENTRY.replace("    alt: A fixture clip of a grid sorting itself\n", "")
        with self.assertRaises(build.BuildError):
            build.parse_entry(bad, "fixture")

    def test_unknown_media_type_fails_the_build(self):
        bad = FIXTURE_ENTRY.replace("01-screen.png", "01-screen.gif")
        with self.assertRaises(build.BuildError):
            build.parse_entry(bad, "fixture")

    def test_entry_of_eight_media_files_builds(self):
        meta, _ = build.parse_entry(media_entry(8), "fixture")
        self.assertEqual(len(meta["media"]), 8)

    def test_entry_of_nine_media_files_fails_the_build(self):
        with self.assertRaises(build.BuildError):
            build.parse_entry(media_entry(9), "fixture")

    def test_author_must_be_datacrafter(self):
        bad = FIXTURE_OFFICIAL_ENTRY.replace("author: DataCrafter", "author: Someone Else")
        with self.assertRaises(build.BuildError):
            build.parse_entry(bad, "fixture")

    def test_official_showcase_cannot_also_name_a_member(self):
        bad = FIXTURE_OFFICIAL_ENTRY.replace("author: DataCrafter\n",
                                             "author: DataCrafter\ngithub: zz-fixture\n")
        with self.assertRaises(build.BuildError):
            build.parse_entry(bad, "fixture")

    def test_member_entry_needs_member_and_github(self):
        for line in ("member: Test Fixture Person\n", "github: zz-fixture\n"):
            with self.assertRaises(build.BuildError):
                build.parse_entry(FIXTURE_EMPTY_ENTRY.replace(line, ""), "fixture")

    def test_folder_name_with_a_space_fails_the_build(self):
        self.add_entry("005 zz fixture spaced", FIXTURE_OTHER_ENTRY)
        with self.assertRaises(build.BuildError):
            build.build(self.root, self.out)

    def test_refuses_to_clear_a_folder_it_did_not_make(self):
        other = Path(self._tmp.name) / "not-ours"
        other.mkdir()
        (other / "keep.txt").write_text("keep", encoding="utf-8")
        with self.assertRaises(build.BuildError):
            build.build(self.root, other)
        self.assertTrue((other / "keep.txt").is_file())

    def test_text_is_escaped(self):
        tricky = FIXTURE_EMPTY_ENTRY.replace("Nothing recorded yet.", "<script>x</script>")
        self.add_entry(EMPTY, tricky)
        build.build(self.root, self.out)
        for page in (self.read("entries", f"{EMPTY}.html"), self.read("index.html")):
            self.assertNotIn("<script>", page)
            self.assertIn("&lt;script&gt;", page)


class RepositoryBuildTest(unittest.TestCase):
    """The real repository content builds, into a temporary folder."""

    def test_repository_builds(self):
        root = Path(__file__).resolve().parent.parent
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "dist"
            summary = build.build(root, out)
            self.assertGreaterEqual(summary["entries"], 1)
            self.assertGreaterEqual(summary["members"], 1)
            index = (out / "index.html").read_text(encoding="utf-8")
            bakery = "entries/001-nick2468-harbour-street-bakery.html"
            self.assertIn((bakery, "Harbour Street Bakery"), card_links(section(index, "showcases")))
            self.assertIn((bakery, "Harbour Street Bakery"), card_links(section(index, "by-member")))
            # Entry 001's first address still answers, and sends the browser on.
            old = (out / "entries" / "001-nick2468-month-end-on-a-schedule.html").read_text(
                encoding="utf-8")
            self.assertIn('url=001-nick2468-harbour-street-bakery.html', old)


if __name__ == "__main__":
    unittest.main()
