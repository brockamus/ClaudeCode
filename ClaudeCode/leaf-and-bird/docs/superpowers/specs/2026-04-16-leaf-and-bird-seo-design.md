# Leaf & Bird SEO + Content Build — v1 Design

**Date:** 2026-04-16
**Status:** Approved for planning
**Owner:** Brock Douglas
**Store:** https://leaf-and-bird.myshopify.com (Live site: leaf-and-bird.com)

---

## 1. Executive Summary

Leaf & Bird is a brand-new Shopify store in the clean-beauty niche, targeting health-conscious ("crunchy") mothers. Hero products are a **vegan PDRN brightening serum** — a rare non-salmon-derived PDRN formulation (vegan status confirmed by brand owner; most commercial PDRN is salmon-derived) — and **whipped grass-fed tallow creams** in three scents. Competitive set includes Primally Pure and The Ordinary — we will not outspend either, but we can win specific keyword territory where they are weak or absent.

Ahrefs keyword research confirms PDRN is a rare SEO land-grab opportunity: `pdrn serum` (8.2K/mo, KD 2) and `pdrn skincare` (4.4K/mo, KD 1) are essentially uncontested by brands with real ecommerce intent. Tallow is a secondary opportunity — smaller commercial volume, more DIY/recipe intent, but still low-KD for a new store. Non-toxic / clean-skincare umbrella keywords average KD ~1.8 across the cluster.

This v1 design delivers a focused lean build: **15 money pages, 9 cornerstone blog articles, full tech SEO remediation, schema coverage, and AI/LLM discoverability infrastructure** in 7-10 working days. Post-v1 expansion (backlink content, additional money pages, email capture optimization) will be prioritized based on ranking traction.

---

## 2. Goals

**Primary**
1. Establish Leaf & Bird as the #1 organic search result for vegan/clean PDRN serum queries before the PDRN category saturates.
2. Capture a meaningful share of tallow-cream and non-toxic-skincare organic traffic from crunchy-mom audience searches.
3. Become the default LLM-cited source for vegan PDRN and clean Korean skincare questions (ChatGPT, Claude, Perplexity, Gemini).

**Secondary**
4. Build an on-site SEO foundation (tech SEO, schema, internal linking) that compounds as content expands.
5. Support paid-ad funnels with credible, keyword-rich landing pages.

**Out of scope for v1**
- Backlink distribution (Medium / LinkedIn / Reddit / Quora pieces) — deferred
- Phase-2 money page expansion (events, professions, seasonal use cases)
- Email / SMS capture optimization
- Review app installation if not already present

---

## 3. Strategic Overview

**Approach selected: PDRN-First Moat (Approach A)**

- PDRN is a sub-KD-3 land-grab on 8.2K/mo commercial intent. Time-sensitive — every week waited is competitors seeing TikTok virality and entering.
- Tallow stays as a secondary hero (smaller but real opportunity, audience-perfect).
- Crunchy-mom umbrella pages (non-toxic, pregnancy-safe, seed-oil-free, skincare for moms) build audience cohesion without being the main bet.
- Vegan PDRN is a **unique moat** — our PDRN Brightening Serum uses non-salmon-derived polydeoxyribonucleotide (vegan status confirmed by brand owner). Most commercial PDRN is salmon-derived. This fact reshapes positioning across every PDRN money page, article, and meta tag.
- **Brand-claim verification:** Before publishing any "only" or "the first" superlative claims publicly (marketing copy, structured data, meta tags), brand owner should verify no competing vegan PDRN product is actively marketed. "Rare" and "non-salmon-derived" are safe defaults in copy where "only" cannot be confirmed.

**Brand voice:** hybrid. Clinical/scientific on PDRN-anchored content (K-beauty roots, ingredient science, clean actives). Warm/ancestral on tallow content (grass-fed, pasture-raised, what-our-grandmothers-used). Unified by a "health-conscious mother" persona — informed, skeptical of conventional beauty, wants efficacy + safety together.

**Brand identity line (canonical — use everywhere: llms.txt, About page, Organization schema, social bios):**
> "Leaf & Bird is a clean vegan skincare brand making the only non-salmon-derived PDRN serum and whipped grass-fed tallow creams, formulated for health-conscious mothers."

---

## 4. Money Page Architecture (15 pages)

### Principle: Structural Diversity Justified by Intent

Google's Helpful Content Update penalizes scaled/templated content. We use a **module library** — not a single template — and each page selects modules based on its query intent. No two pages look structurally identical.

### Intent-Shape Mapping

| Query Intent | Page Shape |
|---|---|
| Commercial (buy now) | Intro → product grid → benefits → FAQ |
| Informational | Long intro → structured explanation → products near bottom |
| Listicle ("best X") | Ranked list with per-item "best for" callouts |
| Comparison ("X vs Y") | Comparison table primary, products as alternatives |
| Problem-solution | Condition explainer → how ingredient helps → routine → products |
| Audience ("X for Y") | Ingredient avoidance list → persona scenarios → curated products |
| Bridge/niche | Narrative essay → curated picks → why Leaf & Bird fits |

### Module Library (pages pick 4-7 of these)

1. **Intro variants** — short punchy / narrative / question-open / problem-agitate-solution / quote-led / ingredient-led
2. **Product display variants** — standard grid / ranked list / "best for X" tags / comparison table / featured + secondary
3. **Body variants** — H2+H3s / comparison table / ingredient breakdown / numbered routine / myth-busting / scenario-based / expert-quoted / step-by-step / pros-cons
4. **Trust modules** — EWG-style "free from" badges / sourcing story / study citations / customer quotes / certifications
5. **FAQ variants** — accordion / inline Q&A / embedded-per-H2 / quick-answers box
6. **Close variants** — related collections / routine CTA / blog recommendation / bundle CTA

Every page: unique H1, unique intro, unique body prose, 5-7 unique FAQs, full schema. Only the module **mix and order** vary.

### PDRN Pillar (7 pages)

| # | Slug | Primary Keyword | Vol | KD | Shape | Funnels To |
|---|---|---|---|---|---|---|
| 1 | `/collections/pdrn-serum` | pdrn serum | 8.2K | 2 | Commercial | PDRN Brightening Serum |
| 2 | `/collections/pdrn-skincare` | pdrn skincare | 4.4K | 1 | Commercial | PDRN + Peptide Eye |
| 3 | `/collections/best-pdrn-serum` | best pdrn serum | 1.0K | N/A | Listicle | PDRN Brightening Serum |
| 4 | `/collections/pdrn-eye-cream` | pdrn eye cream | 150 | N/A | Commercial | Peptide Eye Gel-Cream (positioned as PDRN-adjacent) |
| 5 | `/collections/pdrn-vs-retinol` | pdrn vs retinol | 200 | N/A | Comparison | PDRN Brightening Serum |
| 6 | `/collections/clean-korean-skincare` | non toxic korean skincare + clean korean skincare | 150+ | 0 | Bridge/niche | PDRN + Vitamin C + Peptide Eye |
| 7 | `/collections/vegan-pdrn-serum` | vegan pdrn + plant based pdrn + pdrn without salmon | ~300-500 combined | near 0 | Commercial + audience | PDRN Brightening Serum |

### Tallow Pillar (4 pages)

| # | Slug | Primary Keyword | Vol | KD | Shape | Funnels To |
|---|---|---|---|---|---|---|
| 8 | `/collections/tallow-cream` | tallow cream | 1.2K | 3 | Commercial | All 3 tallow creams |
| 9 | `/collections/whipped-tallow-face-cream` | whipped tallow face cream + beef tallow face cream | 900 + 800 | 0 / 6 | Commercial | All 3 tallow creams |
| 10 | `/collections/best-tallow-cream` | best tallow cream + best tallow face cream | 60 + 600 | N/A | Listicle | All 3 tallow creams |
| 11 | `/collections/tallow-cream-for-eczema` | tallow cream for eczema | 100 | 1 | Problem-solution | All 3 tallow creams |

### Crunchy-Mom Umbrella (4 pages)

| # | Slug | Primary Keyword | Vol | KD | Shape | Funnels To |
|---|---|---|---|---|---|---|
| 12 | `/collections/non-toxic-skincare` | non toxic skincare | 600 | 6 | Audience | PDRN + Tallow (all) |
| 13 | `/collections/pregnancy-safe-skincare` | pregnancy safe skincare | 1K+ | low | Audience | Tallow + gentle serums |
| 14 | `/collections/seed-oil-free-skincare` | seed oil free skincare | niche | 0 | Audience | Tallow + PDRN |
| 15 | `/collections/clean-skincare-for-moms` | skincare for moms + mom skincare | niche | 0 | Audience | Everything |

### Vegan Positioning Weave

Every PDRN money page (1-7) includes:
- Vegan reference in intro paragraph (natural, not forced)
- "Free from" trust module: *No salmon DNA • No animal derivatives • No parabens • No sulfates • No fragrance • No PEGs*
- FAQ: "Is this PDRN vegan?" with consistent answer
- Link to article #9 (vegan PDRN flagship)

### Content Storage

Collection page content stored in **Shopify metafields** (not `body_html`):
- `seo.h1` — page H1 if different from collection title
- `seo.intro` — hero paragraph
- `seo.body_modules` — JSON array of modules (type + content) that renders diversely
- `seo.faq_json` — FAQ array (source of truth for FAQPage schema)
- `seo.meta_title` / `seo.meta_description` — overrides
- `seo.module_order` — controls module sequence per page for structural diversity

Theme change: modify `sections/main-collection-*.liquid` to render these metafields into the page.

---

## 5. Product Page Optimization (9 SKUs)

### Current State

| Product | Body chars | Action |
|---|---|---|
| PDRN Brightening Serum | 3,345 | Restructure + reposition as vegan/clean-Korean hero |
| Tallow Cream Lemongrass & Lavender | 1,369 | Expand — whipped/grass-fed positioning, ancestral story |
| Tallow Cream Orange & Bergamot | 1,327 | Expand — same |
| Tallow Cream Peaceful Night | 1,386 | Expand — same + sleep/night angle |
| Peptide Eye Gel-Cream | 1,263 | Expand — cross-sell as PDRN routine partner |
| Sleep Plus Collagen Cream | 1,185 | Expand — night-routine positioning |
| Vitamin C Serum | 1,367 | Expand — position as the pure daily vitamin C hero |
| Vitamin Glow Serum | 1,294 | Expand — position as the multi-active brightening/radiance serum |
| Dead Sea Mud | 1,220 | Expand — body / detox / exfoliation positioning |

**Target length:** 2,500-3,500 chars per product (400-600 words).

### Product-Level Module Library

**Core modules (every product gets these)**
1. Hero paragraph (40-70 words, primary keyword, positioning hook)
2. Key ingredients block (structured list with "why it matters" per ingredient)
3. Benefits (3-5 concrete outcomes)
4. How to use (step-by-step)
5. Full INCI ingredient list (transparency)
6. Who it's for / not for
7. FAQ (4-7 real questions)

**Rotating modules (product-dependent)**
- Sourcing story (tallow: pasture-raised, grass-fed)
- Science/study citations (PDRN, peptides, vitamin C)
- Ancestral context (tallow)
- Routine pairing ("pairs with X") — cross-sells
- Before/after or use-case scenarios
- "Free from" badges (phenoxyethanol caveat for PDRN addressed honestly, not hidden)
- Mom-specific reassurance (pregnancy, breastfeeding, baby-safe where true)

### Vitamin C vs. Vitamin Glow Positioning

- **Vitamin C Serum ($20)** → pure/daily vitamin C hero, targets `vitamin c serum` / `natural vitamin c serum` / `clean vitamin c serum`
- **Vitamin Glow Serum ($24.90)** → multi-active brightening/radiance serum, targets `brightening serum` / `glow serum` / `radiance serum` / `even skin tone serum`

Different keyword lanes, no cannibalization. Final positioning verified against actual ingredient lists during content write-up.

### Product Title + H1 Changes

| Current | Proposed |
|---|---|
| PDRN Brightening Serum | Vegan PDRN Brightening Serum |
| Tallow Cream Lemongrass & Lavender | Whipped Grass-Fed Tallow Cream — Lemongrass & Lavender |
| Tallow Cream Orange & Bergamot | Whipped Grass-Fed Tallow Cream — Orange & Bergamot |
| Tallow Cream Peaceful Night | Whipped Grass-Fed Tallow Cream — Peaceful Night |
| Others | Review case-by-case for keyword capture |

**Handles stay unchanged** (existing paths remain valid, no 301s needed).

### Meta Tags

Every product gets a hand-written meta title + meta description. Target: 50-60 chars title, 140-160 chars description. Optimized for click-through, not keyword-stuffing.

### Internal Linking

Every product page:
- Links **up** to 2 parent collection money pages (e.g., PDRN product → `/collections/pdrn-serum` + `/collections/vegan-pdrn-serum`)
- Links **sideways** to 1-2 companion products (routine pairing cross-sells)

### Product Schema

Every product gets:
- `Product` (name, SKU, price, availability, brand, image)
- `Offer` (nested inside Product)
- `AggregateRating` (once reviews exist — confirm review app status during P0)
- `FAQPage` (auto-built from product FAQ metafield)
- `BreadcrumbList`

---

## 6. Blog Content Strategy (9 Cornerstone Articles)

Same structural-diversity principle. Each article's shape matches its SERP intent. Every article internal-links to 3-4 money pages.

### PDRN Cluster (4 articles)

**Article 1 — "What Is PDRN? The Complete Guide"**
- Target: `what is pdrn` (4.8K/mo, KD 3) + `what is pdrn in skincare` (1.9K) + `pdrn meaning` (1.9K)
- Shape: Long-form educational pillar (~1,800-2,200 words)
- Links: `/collections/pdrn-serum`, `/collections/pdrn-skincare`, `/products/pdrn-brightening-serum`

**Article 2 — "Is PDRN Salmon Sperm?"** (rewritten as conversion powerhouse)
- Target: `is pdrn salmon sperm` (400) + `pdrn salmon` (1.9K) + `pdrn salmon dna` (900)
- Shape: Direct-answer Q&A with honest pivot — "Yes… but ours isn't." Explains salmon-derived PDRN across most brands, then pivots to Leaf & Bird's vegan formulation.
- Length: ~900-1,100 words
- Links: `/collections/pdrn-serum`, `/collections/vegan-pdrn-serum`, `/collections/clean-korean-skincare`

**Article 3 — "PDRN vs Retinol: Which Is Right for You?"**
- Target: `pdrn vs retinol` (200) + adjacent comparison queries
- Shape: Comparison article with table top + deep-dive + "choose X if" decision helper
- Length: ~1,200-1,500 words
- Links: `/collections/pdrn-vs-retinol`, `/collections/pdrn-serum`, `/collections/pregnancy-safe-skincare`

**Article 4 — "PDRN Benefits for Skin: What the Science Actually Says"**
- Target: `pdrn benefits` (600) + `pdrn skin benefits` (200) + `what does pdrn do for skin` (800)
- Shape: Benefits listicle with mini-evidence per benefit, study citations
- Length: ~1,100-1,400 words
- Links: `/collections/pdrn-serum`, `/products/pdrn-brightening-serum`, `/collections/pdrn-eye-cream`

### Tallow Cluster (2 articles)

**Article 5 — "How to Make Tallow Face Cream (And Why We Stopped Trying)"**
- Target: `how to make tallow face cream` (700) + `tallow face cream recipe` (600) + `diy tallow face cream` (200) + `how to make beef tallow face cream` (400) — captures ~1.9K/mo DIY-intent traffic and converts it
- Shape: Real recipe first (ranks for recipe intent), then honest narrative pivot to why we switched from DIY to professional formulation, then product pitch
- Length: ~1,400-1,700 words
- Links: `/collections/tallow-cream`, `/collections/whipped-tallow-face-cream`, tallow product pages

**Article 6 — "Beef Tallow for Skin: Benefits, Science, and What to Look For"**
- Target: `beef tallow for skin` (51K parent, long-tail capture) + `tallow for skin` (8.4K) + `tallow cream benefits` + `beef tallow cream benefits`
- Shape: Authoritative evergreen guide — ancestral context, biological mechanism (lipid profile matches human sebum), grass-fed vs grain-fed, safety, how to choose
- Length: ~1,600-1,900 words
- Links: `/collections/tallow-cream`, `/collections/whipped-tallow-face-cream`, `/collections/best-tallow-cream`, `/collections/tallow-cream-for-eczema`

### Crunchy-Mom Cluster (2 articles)

**Article 7 — "Pregnancy-Safe Skincare: The Complete Ingredient Avoidance Guide"**
- Target: `pregnancy safe skincare` + `pregnancy safe skincare routine` + `what skincare to avoid pregnancy`
- Shape: Avoidance guide — "avoid" list first (retinoids, salicylic acid, hydroquinone, essential oils, endocrine disruptors), then "what's actually safe," then our curated products
- Length: ~1,400-1,700 words
- Links: `/collections/pregnancy-safe-skincare`, `/collections/tallow-cream`, `/collections/pdrn-serum` (noting PDRN's pregnancy-safety positioning)

**Article 8 — "Is Korean Skincare Non-Toxic? An Honest Breakdown"**
- Target: `non toxic korean skincare` (150, KD 0) + `is korean skincare non toxic` (30) + `clean korean skincare brands` (parent)
- Shape: Honest myth-busting essay — two voices (K-beauty obsessive + crunchy mom), addresses fragrance/preservatives/synthetic actives, positions PDRN as clean-Korean-skincare bridge
- Length: ~1,200-1,500 words
- Links: `/collections/clean-korean-skincare`, `/collections/vegan-pdrn-serum`, `/collections/pdrn-serum`, `/collections/non-toxic-skincare`

### Vegan Flagship (1 article)

**Article 9 — "Is PDRN Vegan? The Honest Answer (and Why We're the Only One Doing It Clean)"**
- Target: `is pdrn vegan` + `vegan pdrn` + `plant based pdrn` + `pdrn alternatives vegan` + `pdrn without salmon`
- Shape: Honest Q&A + alternatives guide + bold positioning push. Direct answer (most PDRN is salmon-derived), ethical sourcing landscape, vegan alternatives, Leaf & Bird's formulation, strong close with routing to vegan-friendly SKUs.
- Length: ~1,200-1,500 words
- Links: `/collections/vegan-pdrn-serum`, `/collections/pdrn-serum`, `/collections/clean-korean-skincare`, `/collections/non-toxic-skincare`, article #2

### Internal Linking Matrix

- Every money page → links to 2-3 related money pages + 1 blog article
- Every blog article → links to 3-4 money pages + 1-2 other articles
- Creates tight topical cluster per pillar

### Featured Images

AI-generated via Gemini 2.5 Flash Image (multimodal) using actual product photos as visual references for brand consistency. Saved to `/Users/skitch/ClaudeCode/leaf-and-bird/images/` and uploaded to Shopify CDN via Admin API.

---

## 7. Tech SEO + Schema Strategy

### Phase 1 — Live Theme Audit

Live theme: **Konversly-1-5-1-skincare-2** (theme ID 186309509419). Pull files locally, check for:

- Duplicate Organization schema (layout + app-injected)
- Duplicate Product schema (`main-product.liquid` + app)
- Logo-as-H1 (common Shopify default killing home page H1 value)
- OG image protocol (http vs https)
- Canonical tag correctness on paginated / filtered collection URLs
- Meta description fallbacks (defaults to vendor — bad)
- `noindex` on internal search pages
- Breadcrumb rendering + schema
- Sitemap completeness
- Image alt rendering on product grid thumbnails

### Phase 2 — Fix Inline

**Mandatory: backup live theme (unpublished duplicate) before any edits.** Roll-back plan in place. Only then edit.

### Phase 3 — Custom Schema Snippet

Single file: `snippets/lb-seo-schema.liquid` — rendered once in `theme.liquid`, conditionally emits schema per template type.

**Coverage:**
- All templates: `Organization`, `WebSite` with `SearchAction`, `BreadcrumbList`
- Product template: `Product` + `Offer` + optional `AggregateRating` + `FAQPage`
- Collection template: `CollectionPage` + `ItemList` (nested Product/Offer, up to 12) + `FAQPage`
- Article template: `Article` + `Person` (author) + `FAQPage` if applicable
- Page template: `WebPage` + `FAQPage` if applicable

FAQ data source: `seo.faq_json` metafield per resource (array of `{question, answer}`). Snippet reads metafield, emits valid JSON-LD. Keeps content and schema in sync automatically.

### Schema Graph Format

One `@graph` object per page, all entities cross-referenced by `@id`. Clean, valid, no duplicates.

### Phase 4 — Collection Page Content Storage

Metafield-driven (see Section 4, Content Storage). Theme modification: `sections/main-collection-*.liquid` renders metafields.

### Phase 5 — Sitemap + Search Console

- Verify all 15 new collection pages appear in `sitemap.xml`
- Verify 9 articles appear in `sitemap.xml`
- Submit fresh sitemap in Google Search Console (user action — requires verified property access)
- Submit IndexNow ping for Bing (programmatic, Claude handles)

### Phase 6 — Misc

- `robots.txt` — confirm no accidental blocks on new collection URLs
- Canonical tags — self-referential on paginated/filtered collection URLs
- hreflang — not needed (single-market English)
- 404 → 301 audit of existing Shopify redirects
- `noindex` on internal search page if theme lacks it
- Image alt audit — every product grid image, hero image, featured image has alt text
- Core Web Vitals — PageSpeed Insights baseline before/after (theme may carry bloat — address lazy-loading if needed)

---

## 8. AI/LLM Discoverability

### `/llms.txt`

Concise brand summary (~200-300 lines). Structure:
- Brand identity line (canonical, appears everywhere)
- Hero products + defining claims
- Full product list with URL + one-line description each
- Core collections with URL + purpose
- Brand values / "free from" positioning
- Contact + commerce URLs

### `/llms-full.txt`

Deep dump (~2,000-4,000 lines). Structure:
- Brand story + founder (if applicable)
- Every product: title, URL, full INCI ingredient list, benefits, use case, price, size, "free from" claims, FAQ
- Every collection/money page: purpose, curated SKUs, reasoning
- Every article: title, URL, one-paragraph summary, key claims
- Full "free from" matrix per product
- Sourcing transparency (grass-fed tallow origin, PDRN synthesis method)

### `robots.txt` — AI Crawler Allow

Explicit `Allow: /` for: GPTBot, ClaudeBot, PerplexityBot, Google-Extended, AppleBot-Extended, CCBot, Amazonbot.

### LLM-Friendly Content Patterns

Every money page, article, and FAQ follows:
- Direct-answer intro sentence (first paragraph literally answers the query)
- "Leaf & Bird is..." explicit brand statements (entity anchoring)
- Comparison tables (Perplexity cites preferentially)
- Q&A blocks (ChatGPT / Claude quote verbatim)
- Reasoned numbered lists ("X benefits, and why each matters")
- Nuance markers in direct answers ("Yes — but only ours. Here's why.")

### Entity Anchoring

Organization schema includes:
- `description` — the canonical brand identity line
- `sameAs` — all social profiles, Trustpilot, Google Business
- `founder` / `foundingDate` if known
- Explicit `brand` node

### Priority LLM Citation Targets

| Query | Target page |
|---|---|
| "vegan PDRN serum" | `/collections/vegan-pdrn-serum` |
| "is PDRN vegan" | article #9 |
| "best tallow cream for eczema" | `/collections/tallow-cream-for-eczema` |
| "clean Korean skincare brands" | `/collections/clean-korean-skincare` |
| "pregnancy safe PDRN" | article #7 + PDRN page FAQs |

### Monitoring

Monthly manual audit: query ChatGPT, Claude, Perplexity, Gemini for priority queries. Track citation rate as a distinct KPI.

---

## 9. Content Production Workflow

### Cadence

Claude drafts, generates images (Gemini), publishes to Shopify via Admin API in batches. User spot-reviews live in batches, flags what needs rework, Claude iterates next day before next phase.

### Tools

- Shopify Admin API access: credentials in auto-memory (`project_leaf_and_bird.md`), not committed to git
- Shopify store: `leaf-and-bird.myshopify.com`
- Gemini API (image generation): key on file in auto-memory (`reference_gemini_api.md`)
- Local theme path: `/Users/skitch/claude-code/theme/` (lowercase)
- Project root: `/Users/skitch/ClaudeCode/leaf-and-bird/`
- Image output: `/Users/skitch/ClaudeCode/leaf-and-bird/images/`

### Risk Mitigation

- Theme backup (unpublished duplicate) before any theme edit
- Metafield-driven content → easy bulk rollback via API
- Descriptive commit-style notes on theme changes
- Live smoke-test after each phase (load 3-5 pages, schema validator, mobile render check)
- No destructive product operations — all additive/replacement, no deletions

---

## 10. Sequencing (Phases P0–P7)

| Phase | Deliverables | Est. time |
|---|---|---|
| **P0 — Preflight** | Theme backup, tech SEO audit report, Shopify metafield definitions created, `lb-seo-schema.liquid` snippet installed, robots.txt updated, review app status confirmed | 1-2 hrs |
| **P1 — Foundation** | Tech SEO fixes live, `/llms.txt` + `/llms-full.txt` published, Organization + WebSite schema live, brand identity line applied sitewide | 4-6 hrs |
| **P2 — Product pages (9)** | All 9 descriptions rewritten with module library, 4 product renames applied, meta titles/descriptions written, FAQ metafields populated, product-level schema verified | 4-6 hrs |
| **P3 — PDRN money pages (7)** | 7 PDRN collection pages built with diverse structures, metafields populated, internal linking in place, FAQPage schema verified | 8-10 hrs |
| **P4 — Tallow + crunchy-mom money pages (8)** | Remaining 8 collections built with diverse structures | 6-8 hrs |
| **P5 — Blog articles (9)** | All 9 cornerstone articles drafted and published, AI-generated featured images, internal linking, article schema verified | 12-15 hrs |
| **P6 — Nav + submission** | Key collections added to main nav, sitemap resubmission to Google Search Console (user action), IndexNow ping (automated) | 2-3 hrs |
| **P7 — Monitoring** | Weekly index/ranking check, monthly LLM citation audit | ongoing |

**Total active work: 7-10 working days.**

---

## 11. Success Metrics

### Traffic / Ranking

- All 15 collections + 9 articles indexed in Google Search Console within 14 days of publishing
- ≥5 priority keywords in top 20 within 30 days
- ≥10 priority keywords in top 10 within 60 days
- Organic sessions to new pages week-over-week trend up

### Conversion

- CTR on new pages in GSC
- Add-to-cart rate from organic landing pages
- Revenue attributed to organic channel

### LLM Citation (distinct KPI)

- Monthly manual audit: ChatGPT, Claude, Perplexity, Gemini queried for the 5 priority queries
- Citation rate tracked over time
- Accuracy of LLM responses about Leaf & Bird tracked

---

## 12. Out of Scope for v1

- Backlink distribution content (Medium / LinkedIn / Reddit / Quora pieces) — deferred to post-v1
- Phase-2 money page expansion (use-cases, events, professions, seasonal) — picked up after v1 ranking data comes in
- Email / SMS capture optimization on new pages — revisit after organic traffic starts
- Review aggregation app (Loox / Judge.me) — defer to post-v1 unless already installed
- Additional product line expansion
- Custom LLM chatbot / on-site AI
- Paid-ad landing page variants beyond what organic pages already serve

---

## Appendix A — Known Data

**Products (9 active):**
- PDRN Brightening Serum ($32) — hero 1
- Peptide Eye Gel-Cream ($35.99)
- Sleep Plus Collagen Cream ($32.99)
- Vitamin C Serum ($20)
- Vitamin Glow Serum ($24.90)
- Tallow Cream Lemongrass & Lavender ($27) — hero 2
- Tallow Cream Orange & Bergamot ($27) — hero 2
- Tallow Cream Peaceful Night ($27) — hero 2
- Dead Sea Mud ($31.90)

**Collections (current 9 — all thin, will be supplemented not replaced):**
- Best Sellers, Body Care, Face Care, Featured, Home page, Specialty Treatments (custom)
- All Products, Serums, Tallow Collection (smart)

**Pages (current 2):** About, Contact
**Blog (1):** The Leaf & Bird Journal (handle: `journal`)

**Live theme:** Konversly-1-5-1-skincare-2 (ID 186309509419)

**PDRN product ingredient confirmation (vegan — no salmon):**
Aqua, Glycerin, Propanediol, Panthenol, Sodium Hyaluronate, Sodium PCA, **Polydeoxyribonucleotide**, Acetyl Hexapeptide-8, Hydroxyethylcellulose, Phenoxyethanol, Ethylhexylglycerin, Sodium Hydroxide. (No salmon / no animal derivatives.)

---

## Appendix B — Keyword Research Summary

**PDRN cluster commercial volume total:** ~35K+ monthly (commercial intent subset)
**Tallow cluster commercial volume total:** ~5K monthly (after filtering DIY/recipe intent)
**Non-toxic skincare cluster average KD:** ~1.8

**Top PDRN keywords by opportunity:**
- pdrn serum (8.2K, KD 2)
- pdrn skincare (4.4K, KD 1)
- what is pdrn (4.8K, KD 3)
- what is pdrn in skincare (1.9K, KD 6)
- pdrn meaning (1.9K, KD 6)
- best pdrn serum (1.0K)
- pdrn benefits (600)
- pdrn vs retinol (200)
- is pdrn salmon sperm (400)

**Top tallow keywords by commercial intent:**
- tallow cream (1.2K, KD 3)
- whipped tallow face cream (900, KD 0)
- beef tallow face cream (800, KD 6)
- tallow face cream (600, KD 2)
- best tallow face cream (600)
- tallow hand cream (200, KD 0)
- tallow cream for eczema (100, KD 1)

**Unicorn bridge keyword:**
- non toxic korean skincare (150, KD 0) — zero real competition, perfect fit for Leaf & Bird positioning

---

**End of Design**
