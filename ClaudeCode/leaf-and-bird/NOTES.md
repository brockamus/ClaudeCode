# Leaf & Bird SEO Build Notes

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
