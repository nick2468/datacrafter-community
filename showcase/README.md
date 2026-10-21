# The showcase

Every showcase is one folder under [entries/](entries/). `site/build.py` turns each
folder into a card on the index of showcase.datacrafter.net and a page of its own with
the screenshots, clips, captions and text.

## How the site shows them

- **The top grid** holds a card for every showcase. Official showcases come first, then
  member showcases in folder order.
- **The members section** below repeats each member's cards under their name, in the
  order of [MEMBERS.md](../MEMBERS.md). A member with no showcase has no group there.
- **Each card** is one link, named by the showcase's title. It shows a cover image, the
  title, a one-line summary and the author. The cover is the first image in the `media`
  list.
- **Each page** is `entries/<folder>.html` on the site.

## Two kinds of showcase

**A member showcase** is made by a Data Crafter. Its `entry.md` names the member with
`member:` and `github:`. [CONTRIBUTING.md](../CONTRIBUTING.md) has the full steps and
rules.

**An official showcase** is made by DataCrafter Software Labs, not by a member. Its
`entry.md` says `author: DataCrafter` in place of `member:` and `github:`. Everything
else is the same. An official showcase shows in the top grid only, never in the members
section. Its folder name uses `datacrafter` where a member's uses their GitHub handle.

## The front matter

| Field | Member showcase | Official showcase | What it is |
|---|---|---|---|
| `title` | required | required | The name on the card and the page |
| `member` | required | not allowed | The member's name as they want it shown |
| `github` | required | not allowed | The member's GitHub handle |
| `author` | not allowed | `DataCrafter` | Marks an official showcase |
| `version` | required | required | The DataCrafter version the media shows |
| `date` | required | required | The date of the showcase, as YYYY-MM-DD |
| `summary` | optional | optional | One line for the card. Without it, the card shows the caption's first sentence |
| `moved_from` | optional | optional | The folder's old name, after a rename. The old page then sends visitors to the new one |
| `media` | the list | the list | Each item has `file` and `alt` |

The caption follows the closing `---`. Blank lines split it into paragraphs.

A folder name is `<number>-<handle>-<short-title>`, in letters, digits and hyphens. The
build fails on anything else, and on a `moved_from` that clashes with a live folder.

## The DataCrafter tour

The first official showcase is a short tour of DataCrafter for curious visitors: basic
navigation and the key screens. It goes here:

```
showcase/entries/000-datacrafter-tour/
  entry.md
  01-<screen>.png
  ...
```

Its `entry.md` starts like this:

```
---
title: DataCrafter
summary: A short tour of the workspace and its key screens.
author: DataCrafter
version: 0.89.1
date: 2026-10-22
media:
  - file: 01-<screen>.png
    alt: One sentence on what the screenshot shows.
---
One paragraph on what the tour shows.
```

The number `000` puts it first in the folder list. An official showcase leads the top
grid whatever its number, so a later official showcase takes the next free number like
any other entry.

## Harbour Street Bakery

[001-nick2468-harbour-street-bakery](entries/001-nick2468-harbour-street-bakery/) is the
founder's month-end close for a made-up two-shop bakery. It was once two things: a
"platform tour" shown inline on the index, and entry 001, "Month-end pack on a schedule".
Both showed the same scenario, and entry 001's two screenshots were the same files as two
of the tour's. On 2026-10-22 they became one member showcase, credited to the founder as
the member who made it. Its `moved_from` keeps entry 001's old address working.

## Rules

Media in every showcase follows the content rules and media limits in
[CONTRIBUTING.md](../CONTRIBUTING.md). Official showcases follow them too.
