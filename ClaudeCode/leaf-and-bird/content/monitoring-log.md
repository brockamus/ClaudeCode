# Leaf & Bird — Weekly SEO Monitoring Log

Format per week:

```
## YYYY-MM-DD
- Indexed pages: NN / 24
- Ranking spot-checks (incognito Google):
  - "pdrn serum" → position N
  - "vegan pdrn" → position N
  - "whipped tallow face cream" → position N
  - "non toxic korean skincare" → position N
  - "tallow cream for eczema" → position N
- site_sanity.py: OK / N issues
- Sitemap URL count: N
- Notes:
```

## 2026-04-17 (v1 build-completion snapshot)

- **Indexed pages:** 0 / 24 (just published — allow 7-14 days for Google to crawl + index)
- **Ranking spot-checks:** N/A (too early)
- **site_sanity.py:** ✅ OK (24/24 URLs pass all 7 checks: schema, H1, meta description, canonical, HTTPS OG, ≥2 internal links, FAQPage)
- **IndexNow:** 26 URLs submitted (Bing/Yandex will pick up within hours)
- **GSC sitemap:** pending user submission (see `gsc-submission-instructions.md`)
- **Notes:** v1 build complete — 15 money pages + 9 articles + 9 products rewritten + tech SEO + llms.txt + robots.txt. First weekly check scheduled for **2026-04-24**.

## 2026-04-17 (post-launch sanity tick)

- **site_sanity.py:** ✅ OK (24/24 URLs pass all 7 checks)
- **check_links.py:** ✅ OK (0 warnings across 15 money pages; internal-link density healthy — every page has ≥7 collection links, ≥3 product links, ≥1 pillar cluster link)
- **Sitemap URL count:** 54 total (10 products, 24 collections, 5 pages, 15 blog articles) — sitemap.xml + all 4 sub-sitemaps return 200
- **Indexed pages:** 0 / 24 (still early — ~4 hours since IndexNow ping, no GSC submission yet)
- **Ranking spot-checks:** N/A (too early)
- **Notes:** No regressions detected. Kicking off content expansion round 2 this session.

## 2026-04-17 (content expansion round 2 shipped)

- **New money pages (3):**
  - `/collections/vegan-snail-mucin-alternative` (id 526393082155) — primary kw: `vegan snail mucin alternative`
  - `/collections/korean-skincare-without-snail-mucin` (id 526393114923) — primary kw: `korean skincare without snail mucin`
  - `/collections/snail-mucin-vs-pdrn` (id 526393213227) — primary kw: `snail mucin vs pdrn`
- **New blog articles (4):**
  - `/blogs/journal/snail-mucin-alternatives-for-vegans` (id 612228989227)
  - `/blogs/journal/snail-mucin-vs-pdrn-explained` (id 612229021995)
  - `/blogs/journal/pdrn-vs-hyaluronic-acid` (id 612229054763)
  - `/blogs/journal/pdrn-vs-peptides` (id 612229087531)
- **Site totals after round 2:** 18 money pages (was 15) + 13 blog articles (was 9) = 31 URLs in `site_sanity.py`
- **Cross-links added:** `clean-korean-skincare`, `vegan-pdrn-serum`, `is-pdrn-vegan`, `is-korean-skincare-non-toxic` all now link into round-2 cluster for crawl equity
- **site_sanity.py (extended):** ✅ OK (31/31 URLs pass all 7 checks)
- **IndexNow:** 7 new URLs submitted to api.indexnow.org (200), Bing (200), Yandex (202)
- **Schema + FAQPage:** all 4 new articles emit 2 JSON-LD blocks with FAQPage
- **GSC sitemap:** new collections + articles will appear in sub-sitemaps automatically (Shopify regenerates); user still needs to resubmit `/sitemap.xml` in GSC to trigger re-crawl
- **Notes:** Cluster A (snail mucin alternative) is the strongest organic play — targets K-beauty → crunchy-mom bridge with our vegan PDRN moat. Cluster C (PDRN vs X) reinforces PDRN entity authority and supports LLM citation. Expected ranking signal within 2-4 weeks for lowest-competition queries (e.g., `vegan snail mucin alternative`, `korean skincare without snail mucin`).

## 2026-04-17 (checklist-review Tier 1 batch)

Cross-referenced the Bianca Bright 137-item SEO checklist against L&B state. Most "not implemented" items in Bianca Bright are already done in L&B v1 (we built with SEO in mind from day 1). Shipped 5 quick wins:

- **Image optimization** — Converted 13 article PNGs → JPG @ 85% quality (17MB → 3.3MB, 81% reduction). Patched `gen_image.py` to emit JPG going forward.
- **Favicon markup** — Added `<link rel="icon">` + `<link rel="apple-touch-icon">` conditional block to `theme-working/layout/theme.liquid`. Will emit once user uploads a favicon in Shopify Admin → Online Store → Themes → Customize → Theme Settings → Favicon (user action).
- **Thin + orphan audit** — New `scripts/audit_thin_orphan.py`. Zero thin pages (all ≥1500 words). Flagged 7 orphans → fixed via surgical inbound links in 5 v1/round-2 collection drafts. Post-fix: 0 orphans among 31 tracked URLs (1 false positive remaining — reviews page, linked from About which is now tracked; CDN lag).
- **Table of Contents on 13 articles** — Auto-generated from H2s, injected as `<div class="lb-toc">` block after intro paragraph with anchor IDs on all headings. Shopify strips `<nav>` from article bodies; using `<div role="navigation">` works. Verified live.
- **Brand reviews page** — Created `/pages/leaf-and-bird-reviews` (id 171595366699) targeting "leaf and bird reviews" branded query. Defensive SEO to own branded SERP. 22 internal links on page. Populated About page body as well (was empty) with brand identity + link to reviews.
- **IndexNow** — Pinged reviews page to api/Bing/Yandex.

**User actions remaining:**
- Upload favicon asset in theme customizer (markup is wired; waiting on image)
- Check GA4 + GSC installation status (no tracking script visible in homepage HTML)
- GSC sitemap resubmission (instructions at `content/gsc-submission-instructions.md`)

**Deferred (not applicable or needs business decision):**
- EU cookie consent banner (user confirmed no EU business)
- Pinterest Auto Pin (needs Pinterest business account)
- Lead-gen popup (needs lead magnet decision)
- Reviews app install (for AggregateRating schema emission)
- Affiliate program page

**Total tracked URLs in site_sanity.py: 33** (24 v1 + 7 round-2 + 2 info pages). All pass.
