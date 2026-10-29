# Contributing to the DataCrafter community

Thank you for helping. This file says how to report a bug, propose an idea or a concept,
and submit a showcase entry. It also states the rules every contribution follows.

**New to GitHub?** [Your first contribution, step by step](https://www.datacrafter.net/contribute.html) says what to click, in
order, with no GitHub knowledge needed.

## Welcome, and credited

DataCrafter is built by AI from specifications written by people and AI together. This
repository is where bug reports, enhancement ideas, concepts, specification changes and
showcase entries arrive, and they are credited.

Every change to DataCrafter starts from a written specification, and an AI agent builds
from that. A bug report written to the form is most of what that agent needs already.
That is why the forms ask for what they ask for.

The product source is not public yet, so this repository holds no product code and there
is nowhere to send a patch today. If the source is opened later, code contributions will
be welcome too.

## Becoming a Data Crafter

You are a Data Crafter when the founder receives your first contribution: a showcase
entry, a bug report, or an enhancement idea. A showcase entry or a concept posted in
Discussions counts too (see below).

On your first contribution the founder adds your row to [MEMBERS.md](MEMBERS.md). You do
not edit it yourself. Membership comes first. Triage comes later, and a contribution does
not have to be accepted or built for you to be a member. A blank or off-topic issue is
closed and is not a contribution. The founder decides that.

If you want your LinkedIn profile linked from your row, say so in your first contribution.

## Report a bug

1. Open a new Issue and choose the **Bug report** form.
2. Fill in every box: the DataCrafter version, the steps, what you expected, what
   happened, and a screenshot.
3. If the bug shows sensitive data, reproduce it on the Demo instance or with made-up data
   first. The content rules below apply to screenshots in Issues too.

The founder reproduces the bug, triages it and replies in a line. If it is fixed, the
release notes credit you.

## Suggest an enhancement

1. Open a new Issue and choose the **Enhancement idea** form.
2. Describe the problem before the proposal. A clear problem is worth more than a
   detailed solution.
3. Say where you think it fits in the product.

The founder triages it and rules where it fits. It may become a specification ruling or a
roadmap item, credited to you.

## Propose a concept or a specification change

There are two ways. Both count as a contribution, and both are credited to you.

**The easy way: a post in Discussions.** Start a new Discussion in the **Ideas** category.
A form asks for the problem and your idea. Plain words are fine. The founder may turn your
post into a concept file in `concepts/`, credited to you.

**The pull request way**, if you are comfortable with GitHub:

1. Write one Markdown file. Name it after the idea, for example
   `concepts/scheduled-email-delivery.md`.
2. Open a pull request that adds that one file to [concepts/](concepts/). One concept per
   pull request.
3. Tick every box in the pull request template.

The founder reviews it by comment. **A merge means "accepted into the backlog". It is a
promise to consider the concept, not a promise to build it.**

## Submit a showcase entry

There are two ways. Both count as a contribution, and both are credited to you.

**The easy way: a post in Discussions.** Start a new Discussion in the **Show and tell**
category. A form asks what you built, the DataCrafter version, and your screenshots or
clips. The content rules and media limits below still apply. The founder turns your post
into a showcase entry, credited to you.

**The pull request way**, if you are comfortable with GitHub:

1. Make a folder under `showcase/entries/` named
   `<next number>-<your GitHub handle>-<short-title>`, for example
   `002-yourhandle-sales-dashboard`.
2. Put your screenshots and clips in it.
3. Add an `entry.md` with a front matter block and one paragraph of caption:

   ```
   ---
   title: Month-end pack on a schedule
   summary: One line for the card on the showcase index.
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

The `summary` is optional. Without it, the card shows your caption's first sentence.
The first image in `media` is the card's cover.

The `version` and the media are your proof of use. The founder checks the rules and
merges. The merge publishes the entry on the showcase: a card on the index, repeated
under your name in the members section, and a page of its own.
[showcase/README.md](showcase/README.md) has every front matter field, and how official
DataCrafter showcases differ.

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
- At most eight files per entry.
- Alt text on every file, in the `media` list of `entry.md`.

A silent clip of twenty to forty seconds with a one-line caption works well. Windows
Snipping Tool can record the screen, and ShareX is free if you want to trim or add text.

## Contribution licence

You keep the copyright in what you contribute. When you contribute, through a pull
request, an Issue, a Discussion or a comment, you agree to these terms:

1. **A licence to us.** You give DataCrafter Software Labs Pty. Ltd. a free, worldwide,
   permanent licence that you cannot withdraw, to use your contribution in any way. That
   includes copying it, changing it, publishing it, building it into DataCrafter and our
   other products and services, and passing those rights on to others, for example to a
   company that takes over the product. It is not exclusive: you may still use your own
   work however you like.
2. **Editing and credit.** You consent to us editing, shortening or combining your
   contribution, and to using it without naming you. This is your consent under the
   moral rights in Australia's Copyright Act. We aim to credit you in the showcase, the
   members list and the release notes, but credit is our practice, not a condition of
   the licence.
3. **It is yours to give.** You confirm the contribution is your own work, or that you
   may share it, and that it holds nothing you are not allowed to share: no employer's
   confidential information, no client's data, no one else's personal details.
4. **No obligation.** We do not have to use a contribution, pay for it or keep it
   published.

Only DataCrafter Software Labs gets this licence. It gives no one else a right to reuse
your work.

The pull request template has a box to tick for this. A pull request without the box
ticked is not merged.

## Removal

- You can remove your own entry with a pull request.
- The founder may remove any entry.
- Your row in `MEMBERS.md` stays unless you ask for it to go. To ask, open an Issue or
  contact the founder.
- Removing an entry from the showcase does not end the licence above.

## Security problems

Never report a security problem in an Issue. See [SECURITY.md](SECURITY.md).
