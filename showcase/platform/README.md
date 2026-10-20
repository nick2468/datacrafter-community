# Platform tour

A tour of the DataCrafter platform by the founder: screenshots and silent captioned clips,
recorded against the Demo instance.

This folder holds that tour. The showcase site shows it at the top of its index page,
above the member entries. Nothing is here yet. The clips come later.

## How the build reads this folder

`site/build.py` reads this folder the same way it reads a member entry. When an
`entry.md` exists here, with the same front matter as a member entry, the build shows its
title, caption and media at the top of the index page. Until then the build shows only
this file's first paragraph.

Media in this folder follows the content rules and media limits in
[CONTRIBUTING.md](../../CONTRIBUTING.md).
