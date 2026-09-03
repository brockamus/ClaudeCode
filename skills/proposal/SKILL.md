---
name: proposal
description: Build a client-facing marketing growth proposal as a branded HTML artifact — SEO, paid media, or full-funnel engagements. Use when the user asks for a proposal, pitch doc, growth plan, audit report, or scope document for a prospect or client (e.g. "build a proposal for X like we did for Claimaro"). Covers the research pass, the required section order, the honesty rules on data, and the branding pass.
---

# Client Growth Proposal

Produces a single branded HTML page, published as an Artifact, that a prospect can read
end to end and say yes to. Not a deck, not a PDF, not a markdown file.

## 1. Research before writing

Never write a proposal from the meeting notes alone. Prospects can tell. Gather:

- **Their site's real footprint.** `site:domain.com/their-folder` search to get the actual
  indexed page inventory. The gap between pages that exist and services they sell is the
  single most persuasive finding in any proposal.
- **The competitive set.** Search the 2–3 core money terms in their city. Note who owns
  page one — direct competitors vs. directories vs. national suppliers. A SERP held by
  directories is a winnable category; one held by entrenched local competitors is not.
- **Ahrefs**, if units are available: organic keywords, positions, volumes, DR.
  Check `subscription-info-limits-and-usage` first — units run out, and a proposal
  built on fabricated volumes is worse than one that says "measured in week one."
- **Market job values.** Search "<service> cost <city>" to ground ROI talk in published
  ranges you can cite rather than numbers you made up.
- **Their brand.** Colors, tagline, founding story, visual world. If the site is blocked
  by the egress proxy, pull it from search snippets and say so.

## 2. Data honesty (non-negotiable)

The proposal will be read by someone who can check. Rules:

- Never state a ranking position, search volume, ad spend, or traffic number you did not
  verify. Not as an estimate, not as an illustration.
- Anything unverified becomes a **week-one baseline audit deliverable** instead. This is
  a stronger sales move anyway — it makes the audit the first thing they get.
- Cited market ranges (job values, ad benchmarks) must be labeled as market data, not
  as the client's numbers.
- Close with an explicit assumptions section. Naming what you don't know yet builds
  more trust than a document that pretends to know everything.

## 3. Section order

This sequence works because it moves from their reality → their problem → your specific
plan → price, so price lands after value is established.

1. **Masthead** — client, prepared-for/by, date, scope. Compact, no giant hero.
2. **Situation** — where they stand, in plain language, one honest paragraph. Name the
   ceiling they're about to hit.
3. **Verified** — 3–5 hard findings with numbers you actually confirmed. This is the
   credibility section; it proves you did work before asking for money.
4. **Gaps** — 3–5 numbered gaps, each with a "Fix:" line. One gap per real problem;
   don't pad.
5. **The wedge** — the one category or angle they can own now. Every good proposal has a
   single sharp idea, not a list of tactics. Justify why it's winnable.
6. **Target table** — ranked targets with status (No page / Thin / Holding), intent, and
   the asset to build. Rank column is justified numbering; status pills carry the signal.
7. **The plan** — three phases mapped to the engagement length. Phases are genuinely
   sequential, so number them. Each phase gets 5–6 concrete deliverables.
8. **Channels** — how each channel plays its role, with recommended ad spend ranges
   stated as recommendations the client sets.
9. **What success looks like** — specific, checkable claims at the end of the term, plus
   an explicit statement of what the term is *not* enough to accomplish. Underclaiming
   here closes more deals than overclaiming.
10. **Investment** — fee, minimum term, what's included, what you need from them.
11. **Assumptions** — see honesty rules above.
12. **Next step** — one clear action.

## 4. Branding pass

Derive the palette and type from the client's actual brand world, not a generic
consultancy look. Read `artifact-design` first and follow its token structure —
light palette on bare `:root`, dark redefined under both
`@media (prefers-color-scheme: dark)` guarded with `:root:not([data-theme="light"])`
and `:root[data-theme="dark"]`.

Carry at least one detail only this client's world would have — their vernacular, their
units, their document conventions. For a veteran-founded trades brand that means briefing
language and field-report structure; for a SaaS brand it means their product's own
interface language. Never ship the same visual identity twice.

Keep prose at ~68ch, use a mono face for labels/tables/figures, and make every number
tabular. Publish with `Artifact`; title is a short product-style name, never
"Proposal for <Client>".

## 5. Deliverable

Write to `proposals/<client-slug>/proposal.html`, publish as an Artifact, hand the user
the link, and state plainly which numbers are verified and which are pending. Commit the
HTML to the repo so the next proposal has a reference.
