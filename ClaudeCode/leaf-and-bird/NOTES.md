# Leaf & Bird SEO Build Notes

## Domains (corrected 2026-04-16)

- **Live custom domain:** `leafandbird.com` (NO hyphen) ← use this in all curl checks and llms.txt/llms-full.txt URLs
- **Shopify internal:** `leaf-and-bird.myshopify.com` (with hyphen — this is only the admin/backend URL, redirects 301 → leafandbird.com)
- **`leaf-and-bird.com` (hyphenated) does NOT resolve** — earlier plan references to it need to be ignored/corrected at task time

Liquid templates using `{{ shop.url }}` auto-resolve to the correct canonical domain, so the schema snippet is fine. Only hardcoded URLs in `/llms.txt`, `/llms-full.txt`, and verification scripts need the corrected domain.


## Theme IDs (UPDATED 2026-04-16 after user published the backup copy as live)

- **LIVE:** `186951631147` — "Copy of Konversly-1-5-1-skincare-2" (role: main) ← **ALL THEME EDITS TARGET THIS ID**
- **BACKUP (frozen original, rollback target):** `186309509419` — "Konversly-1-5-1-skincare-2" (role: unpublished)
- **Local theme backup:** `theme-backup/` (636 files, pulled 2026-04-16 at commit `55cdf1b` — content identical between the two theme IDs since they were duplicated at the same moment)

### Rollback procedure

If anything goes catastrophic during P1 theme edits:
1. Shopify Admin → Themes → find "Konversly-1-5-1-skincare-2" (id 186309509419)
2. Actions → Publish

The frozen original will become live instantly. Then identify the break and iterate on the (unpublished) edited copy.

## Theme Section Naming (important — customized Konversly, NOT Dawn)

The theme uses non-standard section filenames. When plan tasks reference `main-product.liquid` or similar Dawn-conventional names, the actual files are:
- Product detail section: `sections/shop-product-details.liquid` + `sections/featured-product-details.liquid`
- Collection grid section: `sections/main-collection-product-grid.liquid` (this one matches plan)
- Header: `sections/header.liquid` (duplicate Org + WebSite schema lives here at lines 875 + 900)

Refer to `content/theme-audit-report.md` for the full file:line mapping when doing P1 edits.

## Review App Status

- **App detected:** None (Judge.me CSS selector found in defensive typography fix, but no app installed or active)
- **Location in theme:** `theme-backup/assets/app-typography-fix.css` (lines 24-25, 48-49, 96-97) — defensive selector only, not used
- **Native review capability:** Theme has custom "Reviews" block (sections/shop-product-details.liquid) that supports metafield-driven ratings via `custom.rating` and `custom.rating_count`
- **AggregateRating schema:** Currently does not emit (no product metafields set, no third-party app)
- **Decision:** Do NOT emit AggregateRating from lb-seo-schema.liquid until a review app is installed OR custom metafields are populated on products. If Judge.me or another review app is installed in future, verify it emits its own AggregateRating schema and coordinate to avoid duplication (or conditionally emit only when metafield values exist).

## IndexNow Key

(Populated by Task T6.2 — do NOT commit the key to git.)

## Plan Deviations (sanctioned)

- **T0.6:** Plan specified REST `/metafield_definitions.json` — this endpoint does not exist in Shopify Admin API 2024-10 (metafield **definitions** are GraphQL-only via `metafieldDefinitionCreate`). Implementer correctly deviated to GraphQL. All 13 definitions verified live. Metafield **values** (`/metafields.json` and `/{owner}/{id}/metafields.json`) are still REST and work as-specified in later tasks.
- **T1.4:** No-op. The Konversly theme does NOT emit its own Product schema (audit §2 returned zero hits). Live product pages have exactly 1 JSON-LD `@graph` block — from our own `lb-seo-schema.liquid` snippet — containing Organization + WebSite + BreadcrumbList + Product. No duplicate to remove. Task skipped.
- **T1.10:** Shopify Page handle is `llms-txt-v2` (original `llms-txt` was cache-poisoned during template development). End-user URL `/llms.txt` redirects via Shopify URL redirect to `/pages/llms-txt-v2`. Users see `/llms.txt` in the browser — the v2 handle never exposed. Content-Type is `text/html` (Shopify platform limitation — cannot emit `text/plain` from page templates) but response BODY is clean plain text. Content is hardcoded inside `theme-working/templates/page.llms-txt.liquid` because `{% layout none %}` prevents reading `page.content` — to update content, edit BOTH `content/llms-txt-content.txt` AND the template file, then re-upload.

## Post-build Followups (defer unless urgent)

- **Homepage has no og:image** — the Konversly homepage template doesn't assign `page_image`, so the `{%- if page_image -%}` block in `snippets/meta-tags.liquid` skips emission. Product and article pages render og:image correctly. Fix: in theme customizer, set an explicit social sharing image default; or add a theme-level fallback to meta-tags.liquid. Not blocking SEO; affects social shares of the homepage only.
- **Homepage newsletter H1** — `class="inline-richtext h1 scroll-trigger"` section on the homepage renders as `<h1>`. After T1.5 demoted the logo, this is now the only homepage H1 by default. Acceptable for now; revisit if user wants to set a distinct hero headline as the primary H1.
