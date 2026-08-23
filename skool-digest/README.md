# Skool Digest

Turns a Skool course into a playbook you can act on, so you can stop watching
hour-long videos to find fifteen minutes of substance.

It reads the module structure and text out of the classroom, pulls a transcript
for each video (captions when they exist, speech-to-text when they don't),
extracts the concrete actions and every number stated, collapses the endless
repetition into one dependency-ordered playbook, and — optionally — rewrites
that playbook as a ranked 30-day plan for one of your businesses.

Every bullet keeps its source timestamp, so when a line looks too thin you can
jump to the 90 seconds behind it instead of rewatching the hour.

## Output

Running against a course produces, in `out/<course>/`:

| File | What's in it |
| --- | --- |
| `playbook.md` | Every real action, dependency-ordered, with triggers and prerequisites. Plus where the course contradicts itself, and what's safe to ignore. |
| `numbers.md` | Every price, conversion rate, threshold and benchmark stated anywhere, with sources. |
| `templates.md` | Scripts, post formats, DM openers and offer structures as reusable skeletons. |
| `coverage.md` | Per-module filler ratio, and the short list of modules genuinely worth watching. |
| `plan-<brand>.md` | The playbook rewritten for one specific business, ranked by impact vs effort, with a four-week sequence and the plays it deliberately skipped. |
| `SKILL.md` | The playbook as a Claude Code skill — drop it in `~/.claude/skills/` and Claude applies the method while you work. |

The `.json` next to each is the structured source — the markdown is just a
readable view of it.

## Setup

Node 22+. No npm install for the core tool.

```sh
# transcripts
brew install yt-dlp ffmpeg        # or: pipx install yt-dlp

# crawling (optional — you can also save pages by hand)
npm i -g playwright && playwright install chromium
```

Create `.env` in this directory:

```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...        # only needed for videos without captions
```

## Use

### 1. Get the course in

Skool has no public API, so there are two ways in.

**Crawl it** (automatic). Opens a real browser using a persistent profile kept
in `.browser-profile/`. Log into Skool by hand the first time; the session
sticks for every run after that.

```sh
./skool-digest.mjs crawl "https://www.skool.com/<group>/classroom/<id>"
```

**Or save pages by hand** (no Playwright). In your browser, View Source on each
classroom page, save as `.html`, then:

```sh
./skool-digest.mjs ingest ~/Downloads/*.html --title "Course name"
```

Both write `out/<course>/course.json`. Open it and check the module list looks
right before spending money on the next step.

### 2. Analyse it

```sh
./skool-digest.mjs run out/<course>/course.json --limit 3     # trial run first
./skool-digest.mjs run out/<course>/course.json               # the whole thing
```

Transcripts and extractions are cached in `cache/`, keyed by content — re-runs
and newly added modules cost close to nothing.

### 3. Decide what to actually implement

`playbook.md` is everything the course teaches. `plan-<brand>.md` is the part
worth doing for one business, ranked by impact against effort, with a first
step for each and a four-week sequence — plus the plays it skipped and why.
That is the file that answers "what do I implement".

```sh
./skool-digest.mjs --list-brands
./skool-digest.mjs run out/<course>/course.json --brand homesteadfanatic
# or, against an existing playbook:
./skool-digest.mjs apply out/<course>/playbook.json --brand leafandbird
```

Brand context is read from `brands/*.md` here, or from `../copyroom/brands/`,
so the files Copy Room already uses work unchanged.

### 4. Turn it into a skill

`run` writes `SKILL.md` alongside the rest. To install it:

```sh
mkdir -p ~/.claude/skills/<name> && cp out/<course>/SKILL.md ~/.claude/skills/<name>/
```

To re-emit it after editing the playbook by hand, without paying for the
analysis again:

```sh
./skool-digest.mjs skill out/<course> [--name <skill-name>]
```

## Tests

Ingest-layer regression tests — no network, no API keys, no course needed:

```sh
node test/ingest.test.mjs
node test/skill.test.mjs
```

## Costs

- Captions (YouTube, Loom, most Vimeo): free.
- Speech-to-text where captions are missing: roughly $0.35 per hour of video.
- Analysis: a few dollars for a large course, then near-zero on re-runs thanks
  to the cache.

Use `--no-paid` to stay strictly on free captions and skip anything else.

## Notes

- This is a personal comprehension tool for courses you pay for. Keep the output
  private — don't republish the extracted material or pass the playbook on.
- **Extract before you cancel.** Classroom access dies with the subscription, so
  run this while you still have it.
- **Gated videos need your session.** Course videos are usually unlisted or
  members-only, so an anonymous `yt-dlp` fetch gets a 403 and the module
  transcribes to nothing. `run` defaults to the cookies in the crawler's own
  browser profile; use `--cookies-from-browser chrome` or `--cookies <file>` if
  you ingested pages by hand. The run warns and names every module that had
  video but produced no transcript — never ignore that list, it means the
  playbook is thinner than the course.
- The crawler is the fragile part. Skool is a Next.js app and the tool reads the
  `__NEXT_DATA__` payload rather than the rendered page, which survives cosmetic
  redesigns — but expect to repair it occasionally when they change their data
  shape. The manual `ingest` path is the fallback that always works.
- `lib/claude.mjs` is the only file that talks to the API, over plain `fetch`
  for zero-install parity with `copyroom`. Swap it for `@anthropic-ai/sdk` there
  if you'd rather.
