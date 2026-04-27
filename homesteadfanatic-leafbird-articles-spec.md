# Homestead Fanatic × Leaf & Bird — 10 Article Batch Spec

**Date:** 2026-04-26
**Goal:** Ship 10 cornerstone natural-skincare articles on **homesteadfanatic.com** that feature **leafandbird.com** products as recommendations, in Sarah Kate Wilder's voice, with proper FTC ownership disclosure. Three product clusters: eye peptide cream (4), whipped tallow (3), vegan PDRN serum (3).

**Pivot context:** Originally drafted as L&B Shopify articles. User clarified the batch is for HF (Sarah Kate's WordPress homestead/preparedness site) driving traffic to L&B product pages — content marketing / owner-affiliate model. The Leaf & Bird repo spec at `docs/superpowers/specs/2026-04-26-leaf-and-bird-articles-round-3-design.md` is marked superseded.

---

## Properties Involved

| | |
|---|---|
| **Article home** | https://homesteadfanatic.com (WordPress, GeneratePress theme) |
| **Featured products from** | https://leafandbird.com (Shopify) |
| **Author byline** | Sarah Kate Wilder |
| **HF blog category** | New: "Natural Skincare" sub-category under or beside `Health & Wellness` (cat 18). Or all under cat 18. (Decision: see § Category) |
| **Disclosure relationship** | User co-owns Leaf & Bird. **Material connection. FTC disclosure required at top of every article.** |
| **WP REST credentials** | user `fred`, app password `Md7C 1cWk yhcX jmfs ffin lrZ6` (admin) |
| **L&B product URLs to link** | leafandbird.com/products/peptide-eye-gel-cream • leafandbird.com/products/pdrn-brightening-serum • leafandbird.com/products/tallow-cream-{lemongrass-lavender, orange-bergamot, peaceful-night} |

---

## Article Slate

### Eye Peptide Cream Cluster (4 articles)

Anchor: leafandbird.com/products/peptide-eye-gel-cream ($35.99). Acetyl Tetrapeptide-5, caffeine-free.

| # | Slug | Title (working) | Type | Primary kw | Words |
|---|---|---|---|---|---|
| 1 | `vegan-eye-cream-homesteader-review` | "Why I Switched My Eye Cream — A Crunchy Mom's Honest Review" | Cornerstone first-person | vegan eye cream review | 2,200 |
| 2 | `peptide-eye-cream-pregnancy-safe` | "Pregnancy-Safe Eye Cream: What I Looked For (and Avoided)" | Pregnancy/postpartum | pregnancy safe eye cream | 1,900 |
| 3 | `caffeine-free-eye-cream-why` | "Why I Stopped Using Caffeine Eye Cream After My Third Baby" | Personal angle | caffeine free eye cream | 1,700 |
| 4 | `acetyl-tetrapeptide-5-explained` | "Acetyl Tetrapeptide-5: What This Eye Cream Ingredient Actually Does" | Ingredient deep-dive | acetyl tetrapeptide-5 | 1,800 |

### Tallow Cluster (3 articles)

Anchors: 3 whipped tallow variants ($27 each). Frame: ancestral / homesteader-friendly.

| # | Slug | Title (working) | Type | Primary kw | Words |
|---|---|---|---|---|---|
| 5 | `whipped-tallow-cream-review` | "I Tested Whipped Tallow Cream for 60 Days — Here's My Honest Take" | First-person review | whipped tallow cream review | 2,200 |
| 6 | `beef-tallow-vs-drugstore-moisturizer` | "Beef Tallow vs. Drugstore Moisturizer: A Homesteader's Comparison" | Comparison | tallow vs drugstore moisturizer | 1,900 |
| 7 | `pregnancy-safe-tallow-skincare` | "Pregnancy-Safe Tallow Skincare: What's in It and What to Watch For" | Pregnancy angle | pregnancy safe tallow | 1,800 |

### Vegan PDRN Cluster (3 articles)

Anchor: leafandbird.com/products/pdrn-brightening-serum ($32). Frame: K-beauty efficacy + clean-ingredient values.

| # | Slug | Title (working) | Type | Primary kw | Words |
|---|---|---|---|---|---|
| 8 | `what-is-pdrn-homesteader-take` | "What Is PDRN? A Homesteader's Honest Take on K-Beauty's Hottest Ingredient" | Explainer | what is pdrn | 2,000 |
| 9 | `vegan-pdrn-why-it-matters` | "Vegan PDRN Serum: Why It's Hard to Find (and Why That Matters)" | Moat | vegan pdrn serum | 1,800 |
| 10 | `pdrn-vs-retinol-pregnancy` | "PDRN vs. Retinol During Pregnancy: Why I Made the Switch" | Pregnancy / alternative | pdrn vs retinol pregnancy | 1,900 |

**Total: 10 articles, ~19,200 words**

---

## Category

Default category: **Health & Wellness (id 18)** — already 16 articles, fits Sarah Kate's "natural-health" arc.

Optional: create new sub-category "Natural Skincare" via WP REST taxonomy if user wants a tighter cluster URL. Decision: **default to cat 18 unless user requests new category later.**

---

## Voice Rules

**Author voice = Sarah Kate Wilder.** First person, conversational, learned-the-hard-way. Established persona facts that may be referenced naturally:
- Mom of three
- Texas homestead, 12 acres outside Wimberley
- Started homesteading after the 2021 ice storm
- Pregnancy / postpartum / perimenopause life stages relevant when natural

**Persona facts NOT to invent:** Don't claim Sarah Kate has been using a specific product for an exact duration unless we agree on consistent timeframes upfront. Default safe phrasing: *"I've been testing…"*, *"I switched to…"*, *"In my routine right now…"*. Never claim a specific blood test, dermatologist visit, or medical credential — Sarah Kate is not a medical professional.

**Brand mentions of Leaf & Bird:**
- Refer to Leaf & Bird by name
- Use product names as they appear on leafandbird.com (e.g., "Vegan PDRN Brightening Serum", "Whipped Grass-Fed Tallow Cream")
- Always include the disclosure block at the top of any article that recommends an L&B product

---

## FTC Disclosure Block (required at top of every article)

**Exact disclosure block to insert near top of body, above first H2:**

```html
<div class="hf-disclosure">
  <p><strong>Disclosure:</strong> I co-own Leaf &amp; Bird, the skincare brand featured in this post. My recommendations reflect my honest experience with the products and the reasoning behind why I started the brand in the first place. Other products mentioned (drugstore comparisons, ingredient references) are linked for context only. <a href="https://homesteadfanatic.com/affiliate-disclosure/">Read the full disclosure</a>.</p>
</div>
```

CSS for `.hf-disclosure` already needs to exist in the HF theme or in inline `<style>` block in each article — small light-gray panel, italic, padding, top margin. If site CSS doesn't define it, the article HTML includes a scoped `<style>` snippet.

This wording is honest and compliant. Do **not** weaken to "I may earn a commission" — that's the wrong relationship category.

---

## Per-Article Structure

Same template as the existing GLP-3 / homestead articles (already shipped via the existing HF article publishing pattern):

1. **Hero block**: full-width gradient banner with H1 + tagline + Sarah Kate byline
2. **FTC disclosure block** (above)
3. **TL;DR / Quick Answer** above the fold (40–80 words)
4. **Intro hook**: 80–150 words, story-led
5. **3–6 H2 sections** with structurally diverse layouts (one comparison table where applicable, one bulleted list, one quote/callout). No two articles in the slate share identical H2 ordering.
6. **Product recommendation card** mid-body or near bottom: linked image + product name + 2–3 sentence pitch + "Check it out at Leaf & Bird →" link
7. **FAQ section** (4–6 Q&As, conversational)
8. **Footer CTA** linking to a sibling article in this slate + back to a Health & Wellness category page

**Internal linking:**
- 1–2 outbound links to leafandbird.com/products/{relevant} per article
- 2–3 internal links to other HF articles (existing or sibling in this slate)
- 1 link to existing HF crunchy-mom umbrella content if relevant
- Every article links to at least one of: `pregnancy-safe-skincare-guide`-equivalent on HF (does not yet exist — flag follow-up), the Health & Wellness category, or the GLP-3 pillar (cross-cluster bridge)

**Outbound citations:** Pregnancy-related claims (articles 2, 7, 10) must include at least one cited authoritative source (FDA, ACOG, Mayo Clinic, peer-reviewed PMID). Retinol/peptide claims must cite at least one secondary research source.

---

## Featured Images

Generated via `gen_image.py` using Gemini Imagen 4.0 (key on file in memory).

**Cluster prompt themes:**
- Eye cream cluster: macro of eye area / clean glass dropper / soft cyan-teal accents
- Tallow cluster: golden-hour warm light / beeswax + linen + wood textures / rustic
- PDRN cluster: clean clinical / serum dropper macro / white-on-white

Spec: 1200×630 JPG, descriptive alt text including primary keyword naturally. Upload to WP media library; reference by `source_url`.

---

## Implementation Pipeline

**Authoring location:** `/Users/skitch/hf-leafbird-articles/` (new working dir, parallel to `hf-homepage/` and `hf-seo-ctr-2026-04-26/` which already exist).

**Per-article files:**
```
hf-leafbird-articles/
  manifest.json                       # post-publish: id, slug, link per article
  shared/
    disclosure-block.html             # canonical FTC disclosure HTML
    style.css                         # branded HTML template + .hf-disclosure styles
    voice-guide.md                    # Sarah Kate voice rules + tone examples (for subagents)
  drafts/
    01-vegan-eye-cream-homesteader-review.html
    02-peptide-eye-cream-pregnancy-safe.html
    03-caffeine-free-eye-cream-why.html
    04-acetyl-tetrapeptide-5-explained.html
    05-whipped-tallow-cream-review.html
    06-beef-tallow-vs-drugstore-moisturizer.html
    07-pregnancy-safe-tallow-skincare.html
    08-what-is-pdrn-homesteader-take.html
    09-vegan-pdrn-why-it-matters.html
    10-pdrn-vs-retinol-pregnancy.html
  meta/
    01-{slug}.json                    # title_tag, meta_desc, FAQ JSON-LD payload
    ... (10 total)
  images/
    01-{slug}.jpg                     # featured images, 1200x630
    ...
```

**Publishing steps per article:**
1. Generate featured image → upload to WP media → capture `source_url`
2. POST `/wp/v2/posts` with: `title`, `slug`, `content` (full HTML), `status: publish`, `categories: [18]`, `featured_media: <id>`, `meta._yoast_wpseo_title`, `meta._yoast_wpseo_metadesc`
3. Capture returned `id` + `link` in `manifest.json`
4. Verify HTTP 200 on `link`, FTC disclosure present in rendered HTML, at least 1 leafandbird.com link present

**Site-wide checks after batch:**
- Re-run a HEAD-check pass over each `link` (no 5xx)
- Sanity-check that the new posts appear at https://homesteadfanatic.com/category/health-wellness/
- IndexNow ping (HF doesn't have IndexNow wired today — flag follow-up; do not block on it)

---

## Acceptance Criteria (per article)

- [ ] Word count meets target (±10%)
- [ ] H1 contains primary keyword (variant ok)
- [ ] FTC disclosure block present above first H2
- [ ] At least 1 leafandbird.com product link in body
- [ ] At least 2 internal HF article/category links
- [ ] At least 1 outbound citation if article makes pregnancy or retinol claims
- [ ] FAQPage section has 4–6 Q&As
- [ ] Featured image uploaded with descriptive alt text including primary keyword
- [ ] Post published; HTTP 200 on rendered URL
- [ ] No two articles in this slate share identical H2 sequence
- [ ] Manifest entry recorded with id + slug + link

---

## Out of Scope

- Theme edits to homesteadfanatic.com beyond a single optional `.hf-disclosure` style if the disclosure block needs styling (will inline-style if no theme edit needed)
- Updating the leaf-and-bird Shopify blog (the original superseded scope)
- Building new HF money pages or category pages
- Changes to existing 83 HF posts
- IndexNow wire-up on HF (out of scope; flag follow-up)
- Schema markup beyond what Yoast already emits (Yoast handles Article schema automatically)
- Newsletter / email integration

---

## Reversibility

Each article is a WP post. To revert: set `status: draft` via REST `POST /wp/v2/posts/<id>`. URL stays alive but unpublished. To delete entirely: `DELETE /wp/v2/posts/<id>?force=true`. Manifest tracks all 10 IDs for one-shot revert script.

Featured images can be deleted via `DELETE /wp/v2/media/<id>?force=true` after their parent posts are removed.

---

## Risks

- **Voice drift across 10 articles** — biggest risk. Mitigation: shared `voice-guide.md` referenced in every implementer prompt; spec-compliance review checks voice match.
- **Inadvertent overlap with HF's existing 16 Health & Wellness posts** — most are GLP-3 + general wellness; skincare is greenfield. Verified manually.
- **FTC compliance** — disclosure language is canonical above and must be present. Reviewer check verifies.
- **Cross-link rot** — leafandbird.com URLs are linked from HF. If L&B URLs change later, links break. Mitigation: prefer linking to product pages (stable handles) over collection pages.
- **Image generation rate limits** — Gemini may throttle if 10 images queue at once. Mitigation: generate in batches of 3 with delays.
- **Cannibalization with future L&B own-blog content** — possible but acceptable; HF and L&B target different audiences and have different domain authorities.

---

## Plan Handoff

After this spec is approved, the writing-plans skill produces `/Users/skitch/homesteadfanatic-leafbird-articles-plan.md` with task-level breakdown for the implementer.
