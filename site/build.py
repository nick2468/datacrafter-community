#!/usr/bin/env python3
"""Build the DataCrafter showcase as a static site.

Reads showcase/entries/*/entry.md and MEMBERS.md, and writes plain HTML to
site/dist: an index of showcase cards, one page per showcase, and the members
ledger. Python 3 standard library only, so Cloudflare Pages can
run it with no install step:

    python site/build.py

Options (mainly for the tests):

    --root DIR   the repository root (default: the folder above site/)
    --out DIR    where to write the site (default: <root>/site/dist)

Licensed MIT. See LICENSE, part 2.
"""

import argparse
import html
import re
import shutil
import sys
from pathlib import Path

SITE_TITLE = "The DataCrafter showcase"
COMMUNITY_URL = "https://github.com/nick2468/datacrafter-community"
HOME_URL = "https://www.datacrafter.net"
MARKER = ".built-by-build-py"

IMAGE_TYPES = {".png", ".jpg", ".jpeg"}
VIDEO_TYPES = {".mp4"}
FRONT_MATTER_KEYS = ("title", "version", "date")
MEMBER_KEYS = ("member", "github")

# An official showcase is made by DataCrafter Software Labs, not by a member. Its
# entry.md says "author: DataCrafter" in place of "member:" and "github:". It shows in
# the top grid of the index only, never under a member.
OFFICIAL_AUTHOR = "DataCrafter"
OFFICIAL_NAME = "DataCrafter Software Labs"

SLUG = re.compile(r"[0-9]{3}-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*")

# Colour tokens from www.datacrafter.net's site.css, reused on a dark ground.
STYLE = """
:root{
  --paper:#FAFAF7;
  --ink:#14161A;
  --ink-2:#1B1E25;
  --line-dark:#2A2E37;
  --brass:#A96D14;
  --brass-br:#E0A230;
  --dim:#A9AEB7;
  --sans:"Inter",system-ui,-apple-system,Segoe UI,sans-serif;
  --mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Consolas,monospace;
  --maxw:1120px;
  --gutter:clamp(16px,5vw,56px);
}
*{box-sizing:border-box}
body{margin:0;background:var(--ink);color:var(--paper);font-family:var(--sans);
  font-size:17px;line-height:1.62;-webkit-font-smoothing:antialiased}
a{color:var(--brass-br)}
a:hover{color:var(--paper)}
a:focus-visible{outline:2px solid var(--brass-br);outline-offset:3px}
h1,h2,h3,h4{margin:0 0 12px;font-weight:600;line-height:1.14;letter-spacing:-.021em;color:#fff}
h1{font-size:clamp(30px,4vw,44px)}
h2{font-size:clamp(22px,2.6vw,30px)}
h3{font-size:20px}
p{margin:0 0 14px}
.wrap{max-width:var(--maxw);margin:0 auto;padding-inline:var(--gutter)}
header{border-bottom:1px solid var(--line-dark)}
.nav{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;
  gap:12px 24px;padding-block:18px}
.brand{font-weight:600;font-size:19px;letter-spacing:-.025em;color:#fff;text-decoration:none}
.nav ul{display:flex;flex-wrap:wrap;gap:18px;margin:0;padding:0;list-style:none}
.nav a{text-decoration:none}
main{padding-block:48px 72px}
section{margin-bottom:56px}
.eyebrow{font-family:var(--mono);font-size:12px;font-weight:500;letter-spacing:.15em;
  text-transform:uppercase;color:var(--brass-br);margin-bottom:10px}
.meta{font-family:var(--mono);font-size:13px;color:var(--dim);margin-bottom:18px}
.lede{color:var(--dim);max-width:660px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px}
.cards{margin:0;padding:0;list-style:none}
.card{position:relative;display:flex;flex-direction:column;background:var(--ink-2);
  border:1px solid var(--line-dark);border-radius:4px;padding:16px}
.card:hover{border-color:var(--brass)}
.card:focus-within{outline:2px solid var(--brass-br);outline-offset:3px}
.card .cover{width:100%;aspect-ratio:16/10;object-fit:cover;object-position:left top;margin-bottom:14px}
.card .todo{margin-bottom:14px}
.card h3,.card h4{font-size:20px;margin-bottom:6px}
.card-link{color:#fff;text-decoration:none}
/* The title's link covers the whole card, so the card is one link named by its title. */
.card-link::after{content:"";position:absolute;inset:0}
.card-link:focus-visible{outline:none}
.card:hover .card-link{color:var(--brass-br)}
.summary{color:var(--dim);font-size:15px;margin-bottom:10px}
.byline{font-family:var(--mono);font-size:13px;color:var(--dim);margin:auto 0 0}
.member{margin-top:36px}
.member .meta{margin-bottom:14px}
.media{display:grid;gap:24px;margin-top:24px}
.media figure{margin:0}
img,video{display:block;max-width:100%;height:auto;border:1px solid var(--line-dark);border-radius:4px}
figcaption{font-size:14px;color:var(--dim);margin-top:8px}
.todo{font-family:var(--mono);font-size:14px;color:var(--brass-br);border:1px dashed var(--line-dark);
  border-radius:4px;padding:14px 16px;display:inline-block}
.table-scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:15px}
th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line-dark);white-space:nowrap}
th{font-family:var(--mono);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--dim);font-weight:500}
footer{border-top:1px solid var(--line-dark);padding-block:28px;font-size:14px;color:var(--dim)}
"""


class BuildError(Exception):
    """A problem in the repository content that must fail the build."""


# ---------------------------------------------------------------- parsing


def parse_entry(text, source):
    """Split an entry.md into (front matter dict, caption text).

    The front matter is a small YAML subset: "key: value" lines, and a "media:"
    list whose items each carry "file:" and "alt:". The opening "---" is
    optional; the closing "---" is required.
    """
    lines = text.replace("\r\n", "\n").split("\n")
    if lines and lines[0].strip() == "---":
        lines = lines[1:]
    try:
        end = next(i for i, line in enumerate(lines) if line.strip() == "---")
    except StopIteration:
        raise BuildError(f"{source}: no closing '---' after the front matter")

    meta = {"media": []}
    in_media = False
    for number, raw in enumerate(lines[:end], start=1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        stripped = raw.strip()
        if in_media and raw[:1] in (" ", "\t"):
            if stripped.startswith("- "):
                meta["media"].append({})
                stripped = stripped[2:].strip()
            if not meta["media"]:
                raise BuildError(f"{source}: line {number}: media field before any '- ' item")
            key, value = _split_pair(stripped, source, number)
            meta["media"][-1][key] = value
            continue
        in_media = False
        key, value = _split_pair(stripped, source, number)
        if key == "media":
            if value:
                raise BuildError(f"{source}: line {number}: 'media:' takes a list on the lines below")
            in_media = True
        else:
            meta[key] = value

    for key in FRONT_MATTER_KEYS:
        if not meta.get(key):
            raise BuildError(f"{source}: front matter is missing '{key}'")
    if "author" in meta:
        if meta["author"] != OFFICIAL_AUTHOR:
            raise BuildError(f"{source}: 'author' may only be '{OFFICIAL_AUTHOR}'; "
                             "a member entry uses 'member' and 'github'")
        if any(key in meta for key in MEMBER_KEYS):
            raise BuildError(f"{source}: an official showcase has 'author', not 'member' or 'github'")
    else:
        for key in MEMBER_KEYS:
            if not meta.get(key):
                raise BuildError(f"{source}: front matter is missing '{key}'")
    if meta.get("moved_from") and not SLUG.fullmatch(meta["moved_from"]):
        raise BuildError(f"{source}: 'moved_from' must be an old folder name, "
                         "for example 001-yourhandle-old-title")
    for item in meta["media"]:
        if not item.get("file"):
            raise BuildError(f"{source}: a media item has no 'file'")
        if not item.get("alt"):
            raise BuildError(f"{source}: media '{item['file']}' has no 'alt' text")
        suffix = Path(item["file"]).suffix.lower()
        if suffix not in IMAGE_TYPES | VIDEO_TYPES:
            raise BuildError(f"{source}: media '{item['file']}' is not PNG, JPG or MP4")
        if Path(item["file"]).name != item["file"]:
            raise BuildError(f"{source}: media '{item['file']}' must sit in the entry's own folder")

    caption = "\n".join(lines[end + 1:]).strip()
    return meta, caption


def _split_pair(text, source, number):
    if ":" not in text:
        raise BuildError(f"{source}: line {number}: expected 'key: value'")
    key, value = text.split(":", 1)
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return key.strip(), value


def parse_members(text):
    """Return (headers, rows) from the first Markdown table in MEMBERS.md."""
    table = [line.strip() for line in text.splitlines() if line.strip().startswith("|")]
    if len(table) < 2:
        return [], []
    cells = [[cell.strip() for cell in line.strip("|").split("|")] for line in table]
    headers, body = cells[0], cells[1:]
    rows = [row for row in body if not all(re.fullmatch(r":?-+:?", c) for c in row)]
    return headers, rows


def first_sentence(text):
    """The caption's first sentence, for a card that has no summary of its own."""
    flat = " ".join(text.split())
    return re.split(r"(?<=[.!?])\s", flat, maxsplit=1)[0]


def handle_of(cell):
    """The GitHub handle in a MEMBERS.md cell: the label of [handle](url), or the bare text."""
    match = LINK.search(cell)
    return (match.group(1) if match else cell).strip().lstrip("@")


def paragraphs(text):
    """Plain text to HTML paragraphs. Blank lines separate paragraphs."""
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    return "\n".join(f"<p>{html.escape(' '.join(b.split()))}</p>" for b in blocks)


LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")


def inline_markdown(text):
    """Escape a table cell, turning [text](https://...) into a link."""
    out, pos = [], 0
    for match in LINK.finditer(text):
        out.append(html.escape(text[pos:match.start()]))
        label, url = match.group(1), match.group(2)
        if url.startswith(("https://", "http://")):
            out.append(f'<a href="{html.escape(url)}">{html.escape(label)}</a>')
        else:
            out.append(html.escape(label))
        pos = match.end()
    out.append(html.escape(text[pos:]))
    return "".join(out)


# ---------------------------------------------------------------- reading


def load_entry(folder):
    meta, caption = parse_entry((folder / "entry.md").read_text(encoding="utf-8"),
                                folder / "entry.md")
    present = [m for m in meta["media"] if (folder / m["file"]).is_file()]
    return {
        "slug": folder.name,
        "folder": folder,
        "meta": meta,
        "official": meta.get("author") == OFFICIAL_AUTHOR,
        "summary": meta.get("summary") or first_sentence(caption),
        "caption": caption,
        "present": present,
        "missing": [m for m in meta["media"] if m not in present],
    }


def load_entries(root):
    base = root / "showcase" / "entries"
    if not base.is_dir():
        return []
    folders = sorted(p for p in base.iterdir() if p.is_dir() and (p / "entry.md").is_file())
    return [load_entry(folder) for folder in folders]


def check_slugs(entries):
    """Fail on a folder name the site cannot use, or a moved_from that clashes.

    Returns {old folder name: new folder name} for the redirect pages.
    """
    slugs = {e["slug"] for e in entries}
    moved = {}
    for entry in entries:
        if not SLUG.fullmatch(entry["slug"]):
            raise BuildError(f"showcase/entries/{entry['slug']}: a folder name is "
                             "<number>-<handle>-<short-title>, in letters, digits and hyphens")
        old = entry["meta"].get("moved_from")
        if not old:
            continue
        if old in slugs:
            raise BuildError(f"{entry['slug']}: moved_from '{old}' is still a showcase folder")
        if old in moved:
            raise BuildError(f"{entry['slug']}: moved_from '{old}' is also claimed by {moved[old]}")
        moved[old] = entry["slug"]
    return moved


def group_by_member(entries, headers, rows):
    """Member showcases grouped under each member, in ledger order.

    Returns a list of (name, handle, number, entries). A member with no showcase is
    left out. A showcase whose handle is not in the ledger yet still gets a group,
    after the ledger's, so no card is ever dropped. Official showcases are never here.
    """
    member_entries = [e for e in entries if not e["official"]]

    def cell(row, header):
        index = col.get(header)
        return row[index] if index is not None and index < len(row) else ""

    def showcases_of(handle):
        return [e for e in member_entries if e["meta"]["github"].lower() == handle.lower()]

    col = {h.lower(): i for i, h in enumerate(headers)}
    groups, seen = [], set()
    for row in rows:
        handle = handle_of(cell(row, "github"))
        mine = showcases_of(handle) if handle else []
        if mine and handle.lower() not in seen:
            seen.add(handle.lower())
            groups.append((cell(row, "name") or handle, handle, cell(row, "number"), mine))
    for entry in member_entries:
        handle = entry["meta"]["github"]
        if handle.lower() not in seen:
            seen.add(handle.lower())
            groups.append((entry["meta"]["member"], handle, "", showcases_of(handle)))
    return groups


# ---------------------------------------------------------------- rendering


# The DataCrafter mark, the same one www.datacrafter.net uses. The SVG is drawn inline;
# the PNG (site/static/icon-512.png, copied into the build) is for browsers whose bookmarks
# and home-screen icons only keep a file icon.
ICON_SVG = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Crect width='24' height='24' rx='5' fill='%2314161a'/%3E%3Ccircle cx='7' cy='7' r='2.1' fill='%23e0a230'/%3E%3Ccircle cx='7' cy='17' r='2.1' fill='%23f4f4f0'/%3E%3Ccircle cx='17.5' cy='12' r='2.1' fill='%23f4f4f0'/%3E%3Cpath d='M8.7 8 15.6 10.9M8.7 16 15.6 13.1' stroke='%23f4f4f0' stroke-width='1.3'/%3E%3C/svg%3E"
ICON_PNG = "icon-512.png"


def page(title, body, prefix="", head=""):
    """Wrap a body in the site shell. prefix is the relative path back to the site root."""
    full_title = SITE_TITLE if title == SITE_TITLE else f"{title} | {SITE_TITLE}"
    return f"""<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<link rel="icon" href="{ICON_SVG}">
<link rel="icon" type="image/png" sizes="512x512" href="{prefix}{ICON_PNG}">
<link rel="apple-touch-icon" href="{prefix}{ICON_PNG}">
<style>{STYLE}</style>{head}
</head>
<body>
<header><div class="wrap nav">
  <a class="brand" href="{prefix}index.html">DataCrafter showcase</a>
  <nav aria-label="Site"><ul>
    <li><a href="{prefix}index.html">Showcase</a></li>
    <li><a href="{prefix}members.html">Members</a></li>
    <li><a href="{COMMUNITY_URL}">Community</a></li>
    <li><a href="{HOME_URL}">DataCrafter.net</a></li>
  </ul></nav>
</div></header>
<main class="wrap">
{body}
</main>
<footer><div class="wrap">
  <p>Entries and concepts are CC BY 4.0, credited to the member who made them.
  DataCrafter is built by AI from specifications written by people and AI together.
  <a href="{COMMUNITY_URL}">Contribute words, not code.</a></p>
  <p><a href="{HOME_URL}">Back to www.datacrafter.net</a></p>
</div></footer>
</body>
</html>
"""


def render_media(entry, base):
    """Figures for the media files that exist. base is the URL folder they sit in."""
    figures = []
    for item in entry["present"]:
        src = html.escape(f"{base}{item['file']}")
        alt = html.escape(item["alt"])
        if Path(item["file"]).suffix.lower() in VIDEO_TYPES:
            tag = (f'<video controls preload="metadata" src="{src}" aria-label="{alt}">'
                   f'<a href="{src}">{alt}</a></video>')
        else:
            # Linked to the full-size file, so a phone can open it to read the detail.
            tag = f'<a href="{src}"><img src="{src}" alt="{alt}" loading="lazy"></a>'
        figures.append(f"<figure>{tag}<figcaption>{alt}</figcaption></figure>")
    if entry["missing"] or not entry["present"]:
        figures.append('<p class="todo">media to come</p>')
    return '<div class="media">\n' + "\n".join(figures) + "\n</div>"


def author_name(entry):
    return OFFICIAL_NAME if entry["official"] else entry["meta"]["member"]


def entry_meta_line(entry):
    meta = entry["meta"]
    if entry["official"]:
        who = html.escape(OFFICIAL_NAME)
    else:
        handle = html.escape(meta["github"])
        who = (f'{html.escape(meta["member"])} '
               f'(<a href="https://github.com/{handle}">@{handle}</a>)')
    return (f'<p class="meta">{who} | DataCrafter {html.escape(meta["version"])}'
            f' | {html.escape(meta["date"])}</p>')


def render_entry_page(entry):
    meta = entry["meta"]
    eyebrow = "Official showcase" if entry["official"] else "Member showcase"
    body = f"""<article>
<p class="eyebrow">{eyebrow}</p>
<h1>{html.escape(meta["title"])}</h1>
{entry_meta_line(entry)}
{paragraphs(entry["caption"])}
{render_media(entry, entry["slug"] + "/")}
</article>
<p><a href="../index.html">Back to the showcase</a></p>"""
    return page(meta["title"], body, prefix="../")


def render_redirect(entry):
    """A page at a showcase's old address that sends the browser on to the new one."""
    target = html.escape(f"{entry['slug']}.html")
    head = (f'\n<meta http-equiv="refresh" content="0; url={target}">'
            f'\n<link rel="canonical" href="{target}">')
    body = f"""<section>
<p class="eyebrow">Moved</p>
<h1>This showcase has moved</h1>
<p>{html.escape(entry["meta"]["title"])} is now at <a href="{target}">its new page</a>.</p>
</section>"""
    return page(entry["meta"]["title"], body, prefix="../", head=head)


def render_card(entry, level=3):
    """One showcase as a card. The whole card is one link, named by the title.

    The cover is decorative (alt=""), because the title already names the link and
    the showcase page carries every picture with its own alt text.
    """
    meta = entry["meta"]
    href = f"entries/{html.escape(entry['slug'])}.html"
    images = [m for m in entry["present"] if Path(m["file"]).suffix.lower() in IMAGE_TYPES]
    if images:
        src = html.escape(f"entries/{entry['slug']}/{images[0]['file']}")
        cover = f'<img class="cover" src="{src}" alt="" loading="lazy">'
    else:
        cover = '<p class="todo">media to come</p>'
    return f"""<li class="card">
{cover}
<h{level}><a class="card-link" href="{href}">{html.escape(meta["title"])}</a></h{level}>
<p class="summary">{html.escape(entry["summary"])}</p>
<p class="byline">By {html.escape(author_name(entry))}</p>
</li>"""


def render_cards(entries, level=3):
    cards = "\n".join(render_card(e, level) for e in entries)
    return f'<ul class="grid cards">\n{cards}\n</ul>'


def render_index(entries, groups):
    # Official showcases lead the grid. The rest keep their folder order.
    ordered = [e for e in entries if e["official"]] + [e for e in entries if not e["official"]]
    grid = render_cards(ordered) if ordered else "<p>No showcases yet.</p>"
    parts = []
    for name, handle, number, mine in groups:
        label = f"Data Crafter {html.escape(number)} | " if number else ""
        safe = html.escape(handle)
        parts.append(f"""<div class="member">
<h3>{html.escape(name)}</h3>
<p class="meta">{label}<a href="https://github.com/{safe}">@{safe}</a></p>
{render_cards(mine, level=4)}
</div>""")
    by_member = "\n".join(parts) if parts else "<p>No member showcases yet.</p>"
    body = f"""<section>
<p class="eyebrow">DataCrafter</p>
<h1>{SITE_TITLE}</h1>
<p class="lede">Screenshots and silent clips of DataCrafter at work. Pick a showcase to
see its screens. Showcases made by members of the DataCrafter community are grouped by
member below.</p>
</section>
<section aria-labelledby="showcases">
<p class="eyebrow">Showcases</p>
<h2 id="showcases">Every showcase</h2>
{grid}
</section>
<section aria-labelledby="by-member">
<p class="eyebrow">Members</p>
<h2 id="by-member">Built by Data Crafters</h2>
{by_member}
</section>"""
    return page(SITE_TITLE, body)


def render_members(headers, rows):
    count = len(rows)
    noun = "member" if count == 1 else "members"
    head = "".join(f'<th scope="col">{html.escape(h)}</th>' for h in headers)
    body_rows = "\n".join(
        "<tr>" + "".join(f"<td>{inline_markdown(cell)}</td>" for cell in row) + "</tr>"
        for row in rows)
    body = f"""<section>
<p class="eyebrow">The ledger</p>
<h1>Members</h1>
<p class="lede">You are a Data Crafter when the founder receives your first contribution:
a showcase entry, a bug report, or an enhancement idea. {count} {noun} so far.</p>
<div class="table-scroll"><table>
<thead><tr>{head}</tr></thead>
<tbody>
{body_rows}
</tbody>
</table></div>
</section>"""
    return page("Members", body)


# ---------------------------------------------------------------- writing


def prepare_out(out):
    """Empty the output folder, but only if this script made it.

    The folder itself is kept and only its contents removed, because Windows
    will not delete a folder that another process (a preview server) has open.
    """
    if out.exists():
        if any(out.iterdir()) and not (out / MARKER).exists():
            raise BuildError(f"{out} is not empty and was not made by build.py; refusing to clear it")
        for child in out.iterdir():
            if child.is_dir() and not child.is_symlink():
                shutil.rmtree(child)
            else:
                child.unlink()
    out.mkdir(parents=True, exist_ok=True)
    (out / MARKER).write_text("This folder is generated by site/build.py.\n", encoding="utf-8")


def copy_media(entry, dest):
    for item in entry["present"]:
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(entry["folder"] / item["file"], dest / item["file"])


def build(root, out):
    """Build the site. Returns a short summary dict."""
    root, out = Path(root), Path(out)
    entries = load_entries(root)
    moved = check_slugs(entries)
    members_file = root / "MEMBERS.md"
    headers, rows = parse_members(members_file.read_text(encoding="utf-8")) \
        if members_file.is_file() else ([], [])

    prepare_out(out)
    static = Path(__file__).resolve().parent / "static"
    if (static / ICON_PNG).is_file():
        shutil.copy2(static / ICON_PNG, out / ICON_PNG)
    groups = group_by_member(entries, headers, rows)
    (out / "index.html").write_text(render_index(entries, groups), encoding="utf-8")
    (out / "members.html").write_text(render_members(headers, rows), encoding="utf-8")
    (out / "entries").mkdir()
    by_slug = {e["slug"]: e for e in entries}
    for entry in entries:
        (out / "entries" / f"{entry['slug']}.html").write_text(render_entry_page(entry),
                                                               encoding="utf-8")
        copy_media(entry, out / "entries" / entry["slug"])
    for old, new in moved.items():
        (out / "entries" / f"{old}.html").write_text(render_redirect(by_slug[new]),
                                                     encoding="utf-8")

    return {
        "entries": len(entries),
        "official": sum(1 for e in entries if e["official"]),
        "members": len(rows),
        "media": sum(len(e["present"]) for e in entries),
        "to_come": sum(len(e["missing"]) for e in entries),
        "redirects": len(moved),
    }


def main(argv=None):
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Build the DataCrafter showcase site.")
    parser.add_argument("--root", type=Path, default=here.parent)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    out = args.out or args.root / "site" / "dist"
    try:
        summary = build(args.root, out)
    except BuildError as err:
        print(f"build.py: {err}", file=sys.stderr)
        return 1
    def count(n, one, many):
        return f"{n} {one if n == 1 else many}"

    print(f"Built {out}: {count(summary['entries'], 'showcase', 'showcases')} "
          f"({summary['official']} official), "
          f"{count(summary['members'], 'member', 'members')}, "
          f"{count(summary['media'], 'media file', 'media files')}, {summary['to_come']} to come, "
          f"{count(summary['redirects'], 'redirect', 'redirects')}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
