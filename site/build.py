#!/usr/bin/env python3
"""Build the DataCrafter showcase as a static site.

Reads showcase/platform/, showcase/entries/*/entry.md and MEMBERS.md, and writes
plain HTML to site/dist. Python 3 standard library only, so Cloudflare Pages can
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
MARKER = ".built-by-build-py"

IMAGE_TYPES = {".png", ".jpg", ".jpeg"}
VIDEO_TYPES = {".mp4"}
FRONT_MATTER_KEYS = ("title", "member", "github", "version", "date")

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
h1,h2,h3{margin:0 0 12px;font-weight:600;line-height:1.14;letter-spacing:-.021em;color:#fff}
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
.card{background:var(--ink-2);border:1px solid var(--line-dark);border-radius:4px;padding:20px}
.card h3 a{color:#fff;text-decoration:none}
.card h3 a:hover{color:var(--brass-br)}
.card img{margin-bottom:14px}
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


def load_platform(root):
    """The platform tour: an entry.md if one exists, else the README's first paragraph."""
    folder = root / "showcase" / "platform"
    if (folder / "entry.md").is_file():
        return {"entry": load_entry(folder), "intro": ""}
    intro = ""
    readme = folder / "README.md"
    if readme.is_file():
        text = readme.read_text(encoding="utf-8")
        body = "\n".join(l for l in text.splitlines() if not l.startswith("#"))
        blocks = [b for b in re.split(r"\n\s*\n", body) if b.strip()]
        intro = blocks[0] if blocks else ""
    return {"entry": None, "intro": intro}


# ---------------------------------------------------------------- rendering


# The DataCrafter mark, the same one www.datacrafter.net uses. The SVG is drawn inline;
# the PNG (site/static/icon-512.png, copied into the build) is for browsers whose bookmarks
# and home-screen icons only keep a file icon.
ICON_SVG = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Crect width='24' height='24' rx='5' fill='%2314161a'/%3E%3Ccircle cx='7' cy='7' r='2.1' fill='%23e0a230'/%3E%3Ccircle cx='7' cy='17' r='2.1' fill='%23f4f4f0'/%3E%3Ccircle cx='17.5' cy='12' r='2.1' fill='%23f4f4f0'/%3E%3Cpath d='M8.7 8 15.6 10.9M8.7 16 15.6 13.1' stroke='%23f4f4f0' stroke-width='1.3'/%3E%3C/svg%3E"
ICON_PNG = "icon-512.png"


def page(title, body, prefix=""):
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
<style>{STYLE}</style>
</head>
<body>
<header><div class="wrap nav">
  <a class="brand" href="{prefix}index.html">DataCrafter showcase</a>
  <nav aria-label="Site"><ul>
    <li><a href="{prefix}index.html">Showcase</a></li>
    <li><a href="{prefix}members.html">Members</a></li>
    <li><a href="{COMMUNITY_URL}">Community</a></li>
  </ul></nav>
</div></header>
<main class="wrap">
{body}
</main>
<footer><div class="wrap">
  <p>Entries and concepts are CC BY 4.0, credited to the member who made them.
  DataCrafter is built by AI from specifications written by people and AI together.
  <a href="{COMMUNITY_URL}">Contribute words, not code.</a></p>
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


def entry_meta_line(meta):
    member = html.escape(meta["member"])
    handle = html.escape(meta["github"])
    return (f'<p class="meta">{member} (<a href="https://github.com/{handle}">@{handle}</a>)'
            f' | DataCrafter {html.escape(meta["version"])}'
            f' | {html.escape(meta["date"])}</p>')


def render_entry_page(entry):
    meta = entry["meta"]
    body = f"""<article>
<p class="eyebrow">Member entry</p>
<h1>{html.escape(meta["title"])}</h1>
{entry_meta_line(meta)}
{paragraphs(entry["caption"])}
{render_media(entry, entry["slug"] + "/")}
</article>
<p><a href="../index.html">Back to the showcase</a></p>"""
    return page(meta["title"], body, prefix="../")


def render_card(entry):
    meta = entry["meta"]
    href = f"entries/{html.escape(entry['slug'])}.html"
    thumb = ""
    images = [m for m in entry["present"] if Path(m["file"]).suffix.lower() in IMAGE_TYPES]
    if images:
        src = html.escape(f"entries/{entry['slug']}/{images[0]['file']}")
        thumb = f'<img src="{src}" alt="{html.escape(images[0]["alt"])}" loading="lazy">'
    elif not entry["present"]:
        thumb = '<p class="todo">media to come</p>'
    return f"""<div class="card">
{thumb}
<h3><a href="{href}">{html.escape(meta["title"])}</a></h3>
{entry_meta_line(meta)}
</div>"""


def render_index(platform, entries):
    if platform["entry"]:
        tour = platform["entry"]
        platform_html = (f'<h2>{html.escape(tour["meta"]["title"])}</h2>\n'
                         f'{entry_meta_line(tour["meta"])}\n{paragraphs(tour["caption"])}\n'
                         f'{render_media(tour, "platform/")}')
    else:
        platform_html = ("<h2>The platform</h2>\n"
                         f'<div class="lede">{paragraphs(platform["intro"])}</div>\n'
                         '<p class="todo">media to come</p>')
    if entries:
        cards = '<div class="grid">\n' + "\n".join(render_card(e) for e in entries) + "\n</div>"
    else:
        cards = "<p>No member entries yet.</p>"
    body = f"""<section>
<p class="eyebrow">DataCrafter</p>
<h1>{SITE_TITLE}</h1>
<p class="lede">Screenshots and silent clips of DataCrafter at work: first the platform
tour, then builds shown by members of the DataCrafter community.</p>
</section>
<section aria-labelledby="platform">
<p class="eyebrow" id="platform">Platform tour</p>
{platform_html}
</section>
<section aria-labelledby="entries">
<p class="eyebrow" id="entries">Member entries</p>
<h2>Built by Data Crafters</h2>
{cards}
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
    platform = load_platform(root)
    entries = load_entries(root)
    members_file = root / "MEMBERS.md"
    headers, rows = parse_members(members_file.read_text(encoding="utf-8")) \
        if members_file.is_file() else ([], [])

    prepare_out(out)
    static = Path(__file__).resolve().parent / "static"
    if (static / ICON_PNG).is_file():
        shutil.copy2(static / ICON_PNG, out / ICON_PNG)
    (out / "index.html").write_text(render_index(platform, entries), encoding="utf-8")
    (out / "members.html").write_text(render_members(headers, rows), encoding="utf-8")
    if platform["entry"]:
        copy_media(platform["entry"], out / "platform")
    (out / "entries").mkdir()
    for entry in entries:
        (out / "entries" / f"{entry['slug']}.html").write_text(render_entry_page(entry),
                                                               encoding="utf-8")
        copy_media(entry, out / "entries" / entry["slug"])

    return {
        "entries": len(entries),
        "members": len(rows),
        "media": sum(len(e["present"]) for e in entries),
        "to_come": sum(len(e["missing"]) for e in entries),
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

    print(f"Built {out}: {count(summary['entries'], 'entry', 'entries')}, "
          f"{count(summary['members'], 'member', 'members')}, "
          f"{count(summary['media'], 'media file', 'media files')}, {summary['to_come']} to come.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
