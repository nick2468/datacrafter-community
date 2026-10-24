# The DataCrafter community

This repository is the home of the DataCrafter community. It holds bug reports,
enhancement ideas, concept documents and showcase entries. It also holds the member
ledger and the small script that builds the DataCrafter showcase site.

It holds no product code, and it accepts none.

## Why words, not code

DataCrafter is built by AI from specifications written by people and AI together. People
conceived it. People and AI specified it. AI wrote the code.

So the product code stays private, and that is not secrecy. The project does not want
human code. A patch would have to be turned back into a specification before an AI agent
could own it, so there is nothing for a pull request of code to improve.

What the project wants is words:

- a bug described well enough to reproduce,
- an enhancement idea that states the problem first,
- a concept or a specification change, written as one Markdown file,
- a showcase entry that shows something you built.

We do not accept code. We accept well-written bug reports, specification changes and
concepts, and we credit them. Release notes name the person whose report led to a fix.

## Becoming a Data Crafter

**You are a Data Crafter when the founder receives your first contribution: a showcase
entry, a bug report, or an enhancement idea.**

Receipt is enough. Your contribution does not have to be judged good, or built, for you
to be a member. "Received" means it arrived here in the shape its template asks for. A
blank or off-topic issue is closed and does not count. The founder adds your row to
[MEMBERS.md](MEMBERS.md), so you never edit the ledger yourself.

## Where things go

| You want to | Go to |
|---|---|
| Report a bug | A new Issue, from the "Bug report" template |
| Suggest an enhancement | A new Issue, from the "Enhancement idea" template |
| Propose a concept or a spec change | A pull request that adds one `.md` file to [concepts/](concepts/) |
| Show something you built | A pull request that adds one folder under [showcase/entries/](showcase/entries/) |
| Ask a question | Discussions |
| Report a security problem | Private vulnerability reporting. See [SECURITY.md](SECURITY.md). Never an Issue |

[CONTRIBUTING.md](CONTRIBUTING.md) has the details and the rules.

Discussions is not a support desk. The founder answers when they can.

## What is in this repository

```
README.md                       this file
CONTRIBUTING.md                 how to report, propose and submit; the rules
MEMBERS.md                      the ledger: one row per Data Crafter
SECURITY.md                     where security reports go
LICENSE                         the contribution licence for words and pictures; MIT for site/build.py
.github/ISSUE_TEMPLATE/         bug report and enhancement idea templates
.github/PULL_REQUEST_TEMPLATE.md
concepts/                       concept documents, one .md each
showcase/README.md              how the site shows showcases; the front matter fields
showcase/entries/               every showcase, one folder each, member or official
site/build.py                   builds the showcase site from showcase/ and MEMBERS.md
site/test_build.py              a unit test for the build script
```

## The showcase site

`site/build.py` turns `showcase/` and `MEMBERS.md` into a static site in `site/dist`. It
is Python 3 with no third-party packages. The site is served at
`showcase.datacrafter.net`.

To build it on your own machine:

```bash
python site/build.py
```

Then open `site/dist/index.html` in a browser. To run the test:

```bash
python -m unittest discover -s site
```

### How the site is published

The site is the Cloudflare Pages project `datacrafter-showcase`, served at
`showcase.datacrafter.net`. **It is not connected to Git, so merging to `main` publishes
nothing.** To publish, build it locally and upload `site/dist`, from the repository root:

```bash
python site/build.py
npx wrangler@3 pages deploy site/dist --project-name datacrafter-showcase --branch main
```

Run it from a clean checkout of `main`, so the live site matches a commit. Wrangler records
that commit against the deployment. `site/dist` is never committed.

## Licence

Contributors keep the copyright in their entries and concepts, and give DataCrafter
Software Labs a licence to use them (see
[CONTRIBUTING.md](CONTRIBUTING.md#contribution-licence)). No one else gets a licence to
reuse them. The build script is licensed MIT. See [LICENSE](LICENSE).
