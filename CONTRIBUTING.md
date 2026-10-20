# Contributing to the DataCrafter community

Thank you for helping. This file says how to report a bug, propose an idea or a concept,
and submit a showcase entry. It also states the rules every contribution follows.

## No code, words welcome, credited

DataCrafter is built by AI from specifications written by people and AI together. The
project does not accept code, and this repository holds none. It accepts well-written bug
reports, enhancement ideas, concepts, specification changes and showcase entries, and it
credits them.

Your words are the step before a build. Every change to DataCrafter starts as a written
specification, and an AI agent builds from that. A bug report written to the template is
most of what that agent needs already. That is why the templates ask for what they ask for.

## Becoming a Data Crafter

You are a Data Crafter when the founder receives your first contribution: a showcase
entry, a bug report, or an enhancement idea.

On your first contribution the founder adds your row to [MEMBERS.md](MEMBERS.md). You do
not edit it yourself. Membership comes first. Triage comes later, and a contribution does
not have to be accepted or built for you to be a member. A blank or off-topic issue is
closed and is not a contribution. The founder decides that.

If you want your LinkedIn profile linked from your row, say so in your first contribution.

## Report a bug

1. Open a new Issue and choose the **Bug report** template.
2. Fill in every section: the DataCrafter version, the steps, what you expected, what
   happened, and a screenshot.
3. If the bug shows sensitive data, reproduce it on the Demo instance or with made-up data
   first. The content rules below apply to screenshots in Issues too.

The founder reproduces the bug, triages it and replies in a line. If it is fixed, the
release notes credit you.

## Suggest an enhancement

1. Open a new Issue and choose the **Enhancement idea** template.
2. Describe the problem before the proposal. A clear problem is worth more than a
   detailed solution.
3. Say where you think it fits in the product.

The founder triages it and rules where it fits. It may become a specification ruling or a
roadmap item, credited to you.

## Propose a concept or a specification change

1. Write one Markdown file. Name it after the idea, for example
   `concepts/scheduled-email-delivery.md`.
2. Open a pull request that adds that one file to [concepts/](concepts/). One concept per
   pull request.
3. Tick every box in the pull request template.

The founder reviews it by comment. **A merge means "accepted into the backlog". It is a
promise to consider the concept, not a promise to build it.**

## Submit a showcase entry

1. Make a folder under `showcase/entries/` named
   `<next number>-<your GitHub handle>-<short-title>`, for example
   `002-yourhandle-sales-dashboard`.
2. Put your screenshots and clips in it.
3. Add an `entry.md` with a front matter block and one paragraph of caption:

   ```
   ---
   title: Month-end pack on a schedule
   member: Your name as you want it shown
   github: yourhandle
   version: 0.88.0
   date: 2026-10-20
   media:
     - file: 01-workflow.png
       alt: The Workflow editor showing six chained steps
     - file: 02-run-record.mp4
       alt: A run record filling in step by step
   ---
   One paragraph on what the build does and why.
   ```

4. Open a pull request. One pull request is one entry.
5. Tick every box in the pull request template.

The `version` and the media are your proof of use. The founder checks the rules and
merges. The merge publishes the entry on the showcase.

## Content rules for screenshots and clips

These are the standing rules already in the house standards, restated for pictures:

- Only the Demo instance or a scratch fixture. Fake names that cannot match a real record.
- No key values, tokens, URLs with credentials, or internal hostnames in any frame.
- Every screenshot and clip carries a caption and the version it shows, so it ages visibly
  instead of silently.
- Member entries follow the same rules, stated in the repository's CONTRIBUTING file, and
  the founder checks them before merging.

## Media limits

- Formats: PNG, JPG or MP4.
- Images at least 1200 px wide.
- At most 10 MB per file.
- At most six files per entry.
- Alt text on every file, in the `media` list of `entry.md`.

A silent clip of twenty to forty seconds with a one-line caption works well. Windows
Snipping Tool can record the screen, and ShareX is free if you want to trim or add text.

## Contribution licence

You keep the copyright in what you contribute. By opening a pull request with an entry or
a concept, you license it under the
[Creative Commons Attribution 4.0 International licence (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

That lets the showcase show your entry, lets DataCrafter Software Labs reuse a screenshot
in a post with credit to you, and lets a concept be turned into a specification. The pull
request template has a box to tick for this. A pull request without the box ticked is not
merged.

## Removal

- You can remove your own entry with a pull request.
- The founder may remove any entry.
- Your row in `MEMBERS.md` stays unless you ask for it to go. To ask, open an Issue or
  contact the founder.

## Security problems

Never report a security problem in an Issue. See [SECURITY.md](SECURITY.md).
