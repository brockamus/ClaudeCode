# Copy Room — Design

**Date:** 2026-07-13
**Status:** Approved by Brock
**Location:** `~/copyroom/`

## Purpose

A CLI tool that takes a copy brief (FB/TikTok ads, Shopify PDPs, email/newsletter — the brief states the format) and runs three AI models (OpenAI GPT, Anthropic Claude, xAI Grok) in a collaborative loop until they converge on the best version of the copy.

## Usage

```
copyroom --brand leafandbird "FB ad for the PDRN eye cream — angle: pregnancy-safe retinol alternative"
```

| Flag | Default | Meaning |
|---|---|---|
| `--brand <name>` | none | Loads `brands/<name>.md` as shared context for all three models |
| `--rounds <n>` | 3 | Hard cap on refine rounds |
| `--threshold <n>` | 8 | All three models must score the draft ≥ this (1–10) to stop early |

A `copyroom` shell alias points at the script.

## Architecture

Single-file, zero-dependency Node script (`copyroom.mjs`, Node 18+, plain `fetch`). Two request shapes cover all three providers: OpenAI-compatible (OpenAI + xAI) and Anthropic Messages API. Model IDs live in a config block at the top of the script for easy swapping.

```
~/copyroom/
  copyroom.mjs      # everything
  .env              # OPENAI_API_KEY, ANTHROPIC_API_KEY, XAI_API_KEY (git-ignored)
  brands/*.md       # brand voice files, hand-written (voice, audience, offers, banned phrases)
  runs/<date>-<slug>/
    final.md        # winning copy + score table + each model's one-line verdict
    transcript.md   # full debate: all drafts, critiques, revisions per round
```

## The loop (draft → merge → refine)

1. **Draft (parallel):** all three models draft independently from brief + brand file.
2. **Merge:** Claude (fixed merge editor) combines the strongest elements of all three drafts into one candidate.
3. **Refine rounds (up to `--rounds`):**
   - All three models critique the candidate in parallel, returning JSON `{score: 1-10, strengths: [], fixes: []}`.
   - If all scores ≥ threshold → done.
   - Otherwise a rotating editor (round 1: GPT, round 2: Grok, round 3: Claude) revises the candidate using the collected fixes.
4. **Output:** final copy + scores printed to terminal; `final.md` and `transcript.md` written to `runs/`.

Round-by-round scores print live so a run is watchable from the terminal.

## Models & keys

- Model IDs verified against provider docs at build time (api-doc-verification); stored in the top-of-file config block.
- Keys copied into `~/copyroom/.env` from existing project .envs (OpenAI: mediagage / video-clipper; Anthropic: video-clipper; xAI: Persona-Studio). Each key is smoke-tested with a live ping during build since some are old.

## Error handling

- Missing key → clear message naming the provider and where to set it.
- Failed API call → one retry. Provider still down → continue with the remaining two (warning in output and transcript). Fewer than two providers alive → abort.
- Malformed critique JSON → one re-ask; then salvage score via first-number regex, fixes as raw text.

## Out of scope (v1, deleted by the Algorithm pass)

- Copy-type templates (brief carries the format)
- Brand profile schema/generator (a brand is a hand-written markdown file)
- Web UI, streaming output, config system, npm packaging, mock/dry-run mode, test suite

## Verification

One real run on a Leaf & Bird brief; read the transcript and confirm the loop, scoring, convergence, and output files behave as specced.
