# Leaf & Bird Theme SEO Audit

## 1. Organization schema occurrences
- `sections/header.liquid:875` — `"@type": "Organization"`

## 2. Product schema occurrences

## 3. WebSite schema occurrences
- `sections/header.liquid:900` — `"@type": "WebSite"`

## 4. H1 usages in theme
- `snippets/limited-time-sale.liquid:34` — `<h1 `
- `snippets/product-info.liquid:249` — `<h1
`
- `snippets/trustpilot-rating-block.liquid:49` — `<h1 `
- `sections/main-addresses.liquid:21` — `<h1>`
- `sections/main-list-collections.liquid:5` — `<h1 `
- `sections/main-collection-banner.liquid:15` — `<h1 `
- `sections/main-activate-account.liquid:18` — `<h1>`
- `sections/main-search.liquid:69` — `<h1 `
- `sections/header.liquid:564` — `<h1 `
- `sections/header.liquid:607` — `<h1 `
- `sections/main-reset-password.liquid:18` — `<h1>`
- `sections/main-cart-items.liquid:214` — `<h1 `
- `sections/main-cart-items.liquid:282` — `<h1 `
- `sections/main-order.liquid:19` — `<h1 `
- `sections/main-blog.liquid:21` — `<h1 `
- `sections/main-page.liquid:42` — `<h1 `
- `sections/main-login.liquid:22` — `<h1 `
- `sections/main-login.liquid:71` — `<h1 `
- `sections/main-register.liquid:18` — `<h1>`
- `sections/main-article.liquid:49` — `<h1
`
- `sections/listicle.liquid:461` — `<h1 `
- `sections/main-404.liquid:53` — `<h1 `
- `sections/main-password-header.liquid:27` — `<h1 `
- `sections/main-account.liquid:14` — `<h1 `
- `templates/gift_card.liquid:147` — `<h1>`

## 5. Logo-in-header patterns (possible H1 abuse)
- `snippets/product-tabs.liquid:57`
- `snippets/product-info.liquid:145`
- `sections/as-seen-in-logos.liquid:219`
- `sections/shop-product-details.liquid:891`
- `sections/header.liquid:20`
- `sections/photo-feed.liquid:22`
- `sections/custom-footer.liquid:576`
- `sections/footer.liquid:484`
- `sections/main-password-header.liquid:2`
- `sections/main-password-header.liquid:110`
- `sections/main-account.liquid:14`
- `templates/gift_card.liquid:17`

## 6. OG image tags (check for http:// instead of https://)

## 7. Canonical tag references
- `layout/theme.liquid:27` — `rel="canonical"`
- `layout/password.liquid:8` — `rel="canonical"`
- `templates/gift_card.liquid:11` — `rel="canonical"`

## 8. robots meta / noindex

## 9. Image alt attribute usage
- Total `<img` tags: 212
- With `alt=`: 195
- Missing alt: 17

## 10. Meta description usages
- `layout/theme.liquid:59` — `name="description"`
- `layout/password.liquid:20` — `name="description"`
- `templates/gift_card.liquid:25` — `name="description"`

## 11. Existing FAQPage schema

---

## Fix List

> Legend: **FIX** = edit theme in P1 | **KEEP** = correct as-is | **INVESTIGATE** = load live page to confirm

### Category 1 — Organization schema

| File | Line | Classification | Reason |
|------|------|----------------|--------|
| `sections/header.liquid` | 875 | **FIX** | Existing Organization schema block will become a duplicate once `snippets/lb-seo-schema.liquid` is injected in P1. Remove the inline `<script type="application/ld+json">` block for Organization from header.liquid (lines ~871–893). |

### Category 2 — Product schema

| File | Line | Classification | Reason |
|------|------|----------------|--------|
| *(none found)* | — | KEEP | No existing Product schema in theme. P1 will add our own via the new snippet — no conflict. |

### Category 3 — WebSite schema

| File | Line | Classification | Reason |
|------|------|----------------|--------|
| `sections/header.liquid` | 900 | **FIX** | WebSite schema is gated on `request.page_type == 'index'` which is correct logic, but it will duplicate the WebSite schema our `lb-seo-schema.liquid` snippet will emit. Remove the inline `<script type="application/ld+json">` block for WebSite from header.liquid (lines ~896–912) and re-implement in the new snippet so we control the output. |

### Category 4 — H1 usages

| File | Line | Classification | Reason |
|------|------|----------------|--------|
| `snippets/limited-time-sale.liquid` | 34 | **FIX** | A promotional section (used on homepage/landing pages) that contains an `<h1>` for a configurable headline. This will conflict with the page-level H1. Change to `<h2>`. |
| `snippets/product-info.liquid` | 249 | **KEEP** | Product title H1 — this is the primary on-page H1 for product pages. Correct. |
| `snippets/trustpilot-rating-block.liquid` | 49 | **FIX** | A reusable rating widget snippet containing an `<h1>` for the Trustpilot "5-star" text. This snippet can render alongside a real page-level H1. Change to `<h2>` or `<p>`. |
| `sections/main-addresses.liquid` | 21 | **KEEP** | Customer account addresses page — single H1 as page title. Correct for non-indexed page. |
| `sections/main-list-collections.liquid` | 5 | **KEEP** | Collections listing page H1. Single H1 as page title. Correct. |
| `sections/main-collection-banner.liquid` | 15 | **KEEP** | Collection page banner H1 rendering `collection.title`. This is the primary H1 for collection pages. Correct. |
| `sections/main-activate-account.liquid` | 18 | **KEEP** | Account activation page H1. Non-indexed account page, correct. |
| `sections/main-search.liquid` | 69 | **KEEP** | Search results page H1 ("Search" heading). Single H1. Correct. |
| `sections/header.liquid` | 564 | **KEEP** | Logo wrapped in `<h1>` but only emitted when `request.page_type == 'index'` (homepage). This is the standard Shopify Dawn pattern — logo-in-H1 on homepage only, which is acceptable SEO practice as long as alt text is set. Verify alt. |
| `sections/header.liquid` | 607 | **KEEP** | Second logo-in-H1 block for `logo_position == 'middle-center'` layout variant — same conditional as above, homepage only. Same status as :564. |
| `sections/main-reset-password.liquid` | 18 | **KEEP** | Password reset page H1. Non-indexed, correct. |
| `sections/main-cart-items.liquid` | 214 | **KEEP** | Cart page "Your cart" H1. Single H1 per page. Correct. |
| `sections/main-cart-items.liquid` | 282 | **INVESTIGATE** | "Your cart is empty" H1 inside the same cart template. Two H1s can exist on the same cart page (one is hidden via CSS when cart has items). Confirm only one is visible at a time — if both can be visible simultaneously, change the empty-state one to `<h2>`. |
| `sections/main-order.liquid` | 19 | **KEEP** | Order confirmation/detail page H1. Non-indexed, correct. |
| `sections/main-blog.liquid` | 21 | **KEEP** | Blog listing page H1 rendering `blog.title`. Single H1. Correct. |
| `sections/main-page.liquid` | 42 | **KEEP** | Generic page template H1 rendering `page.title`. Single H1. Correct. |
| `sections/main-login.liquid` | 22 | **KEEP** | Login page "Forgot password" H1 — inside a toggle region (shown/hidden via anchor). Only one H1 is visible at a time by design (password recovery form vs. login form). Acceptable for non-indexed page. |
| `sections/main-login.liquid` | 71 | **KEEP** | Login form H1 — counterpart to :22. See above. Non-indexed page. |
| `sections/main-register.liquid` | 18 | **KEEP** | Registration page H1. Non-indexed, correct. |
| `sections/main-article.liquid` | 49 | **KEEP** | Blog article page H1 rendering `article.title`. This is the primary H1 for article pages. Correct. |
| `sections/listicle.liquid` | 461 | **INVESTIGATE** | Custom listicle section with a configurable H1 title block. This section may be placed on pages that already have a page-level H1 from another section. Check which templates use `listicle` — if it co-exists with `main-page.liquid` on the same page, change to `<h2>`. |
| `sections/main-404.liquid` | 53 | **KEEP** | 404 page H1. Single H1. Correct. |
| `sections/main-password-header.liquid` | 27 | **KEEP** | Password/coming-soon page H1. Non-indexed page. Correct. |
| `sections/main-account.liquid` | 14 | **KEEP** | Account dashboard H1 rendering customer name / "Account" title. Non-indexed, correct. |
| `templates/gift_card.liquid` | 147 | **KEEP** | Gift card page H1 showing balance. Single H1. Correct. |

### Category 5 — Logo-in-header patterns

| File | Line | Classification | Reason |
|------|------|----------------|--------|
| `snippets/product-tabs.liquid` | 57 | **KEEP** | Pattern match was a false positive — context is a star SVG path inside a product comparison table. No H1 wrapping logo. |
| `snippets/product-info.liquid` | 145 | **KEEP** | Regex matched on unrelated "logo" text in a comparison section variable. No H1-wrapped logo. |
| `sections/as-seen-in-logos.liquid` | 219 | **KEEP** | Section schema definition text. No H1-wrapped logo. |
| `sections/shop-product-details.liquid` | 891 | **INVESTIGATE** | Load the PDP live to confirm no H1 wraps the logo in this custom section. |
| `sections/header.liquid` | 20 | **KEEP** | This is a CSS class definition (`.scrolled-past-header .header__heading-logo-wrapper`), not an H1-wrapped logo. |
| `sections/photo-feed.liquid` | 22 | **KEEP** | Pattern match on variable name containing "logo" in Liquid assign. No markup issue. |
| `sections/custom-footer.liquid` | 576 | **KEEP** | Footer logo — standard footer image, no H1 wrapping. |
| `sections/footer.liquid` | 484 | **KEEP** | Footer logo — standard footer image, no H1 wrapping. |
| `sections/main-password-header.liquid` | 2 | **KEEP** | Password page header — logo in header, not wrapped in H1 (H1 is the store name/headline below it). |
| `sections/main-password-header.liquid` | 110 | **KEEP** | Second hit in same file — see above. |
| `sections/main-account.liquid` | 14 | **KEEP** | H1 is the account title ("My Account"), not a logo. No H1-wrapped logo. |
| `templates/gift_card.liquid` | 17 | **KEEP** | Gift card template logo area — not wrapped in H1. |

### Category 6 — OG image HTTP vs HTTPS

| Classification | Reason |
|----------------|--------|
| **KEEP** (no action needed) | No HTTP OG image tags found. All OG image references are either HTTPS or use Shopify's `image_url` filter which always returns HTTPS CDN URLs. |

### Category 7 — Canonical tags

| File | Line | Classification | Reason |
|------|------|----------------|--------|
| `layout/theme.liquid` | 27 | **KEEP** | Standard `{{ canonical_url }}` — Shopify-native, correct. |
| `layout/password.liquid` | 8 | **KEEP** | Standard `{{ canonical_url }}` on coming-soon page. Correct. |
| `templates/gift_card.liquid` | 11 | **KEEP** | Canonical on gift card template. Correct. |

### Category 8 — robots meta / noindex

| Classification | Reason |
|----------------|--------|
| **KEEP** (no action needed) | No `name="robots"` or `noindex` found anywhere in the theme. Shopify handles noindex for internal/system pages at the platform level. No theme-level overrides exist. |

### Category 9 — Image alt attributes

> Note: The script's `[^>]*` regex undercounts `alt=` on multi-line `<img>` tags. A corrected multiline scan shows **7 truly missing alt** (not 17). The 10 "false positives" in the script output (article-card, card-product, card-collection, product-media, main-collection-banner, main-article, email-signup-banner) all have `alt=` further down in their multi-line tags.

**Truly missing alt — 7 occurrences:**

| File | Lines | Classification | Reason |
|------|-------|----------------|--------|
| `snippets/frequently_bought_with_product.liquid` | 68, 163, 258, 353, 448, 543 | **FIX** | Product images in the "Frequently Bought With" upsell widget use `img_url` with no `alt` attribute. Add `alt="{{ product.featured_media.alt | escape }}"` to all 6 occurrences. |
| `snippets/estimated-shipping.liquid` | 12 | **FIX** | Custom icon image rendered via `block.settings.custom_icon` has no `alt`. Add `alt="{{ block.settings.icon_alt | default: '' | escape }}"` or an empty `alt=""` if purely decorative. |

### Category 10 — Meta description

| File | Line | Classification | Reason |
|------|------|----------------|--------|
| `layout/theme.liquid` | 59 | **INVESTIGATE** | Meta description uses `{% if page_description %}...{% endif %}` — only outputs a description tag when `page_description` is non-empty. Verify: (a) product/collection/article pages populate `page_description` from their metafields/excerpts, and (b) the homepage and generic pages have descriptions set in Shopify admin. If any page type renders without a description, add a fallback (e.g. `{{ shop.description | default: shop.name }}`). |
| `layout/password.liquid` | 20 | **KEEP** | Password/coming-soon page description. Non-indexed, no priority. |
| `templates/gift_card.liquid` | 25 | **KEEP** | Gift card template description. Non-indexed, no priority. |

### Category 11 — FAQPage schema

| Classification | Reason |
|----------------|--------|
| **KEEP** (no action needed) | No FAQPage schema found in the theme. Our P1 work will add it via `lb-seo-schema.liquid` — no conflict. |

---

## Summary

| Category | Total hits | FIX | KEEP | INVESTIGATE |
|----------|-----------|-----|------|-------------|
| 1. Organization schema | 1 | 1 | 0 | 0 |
| 2. Product schema | 0 | 0 | 0 | 0 |
| 3. WebSite schema | 1 | 1 | 0 | 0 |
| 4. H1 usages | 25 | 2 | 19 | 4 |
| 5. Logo-in-header | 12 | 0 | 11 | 1 |
| 6. OG image HTTP | 0 | 0 | — | 0 |
| 7. Canonical | 3 | 0 | 3 | 0 |
| 8. robots/noindex | 0 | 0 | — | 0 |
| 9. Missing alt (corrected) | 7 | 7 | 0 | 0 |
| 10. Meta description | 3 | 0 | 2 | 1 |
| 11. FAQPage schema | 0 | 0 | — | 0 |
| **TOTAL** | **52** | **11** | **35** | **6** |

### Top 3 Most Important Findings for P1

1. **Schema duplication risk (Categories 1 & 3)** — `sections/header.liquid` contains both an Organization schema block (line 875) and a WebSite schema block (line 900). Both must be removed before we inject `lb-seo-schema.liquid`, otherwise Google will see duplicate structured data and may ignore or penalize both.

2. **Missing alt on product images in upsell widget (Category 9)** — `snippets/frequently_bought_with_product.liquid` has 6 `<img>` tags without `alt` attributes on product images. These are high-visibility (appear on PDPs) and are a direct accessibility + SEO signal failure.

3. **Rogue H1s on promotional snippets (Category 4)** — `snippets/limited-time-sale.liquid:34` and `snippets/trustpilot-rating-block.liquid:49` both use `<h1>` tags for section headlines. These snippets can be placed on any page, silently creating multiple H1s per page and diluting the page's primary heading signal.
