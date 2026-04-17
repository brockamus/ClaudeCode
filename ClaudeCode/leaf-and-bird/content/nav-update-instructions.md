# T6.1 — Main Nav Update (Your Action Required)

The Shopify Admin API token doesn't have the `online_store_navigation` scope, so menu updates can't be done via API. Below is a copy-paste checklist for the Shopify Admin UI.

## Steps

1. Open **Shopify Admin → Online Store → Navigation**
2. Click the **Main menu** to edit
3. Add these menu items (adjust nesting per your preference; flat list works fine to start):

### Recommended additions to Main menu

**New top-level items (or under a "Shop" dropdown):**

| Menu item name | URL |
|---|---|
| PDRN Serum | `/collections/pdrn-serum` |
| Vegan PDRN | `/collections/vegan-pdrn-serum` |
| Tallow Cream | `/collections/tallow-cream` |
| Non-Toxic Skincare | `/collections/non-toxic-skincare` |
| Pregnancy-Safe | `/collections/pregnancy-safe-skincare` |

**Suggested dropdown structure (if you want a cleaner nav):**

- **Shop**
  - All Products (existing)
  - Face Care (existing)
  - Body Care (existing)
  - Best Sellers (existing)
- **PDRN**
  - PDRN Serum
  - Vegan PDRN
  - PDRN Skincare
  - Best PDRN Serum
  - PDRN vs Retinol
- **Tallow**
  - Tallow Cream
  - Whipped Tallow Face Cream
  - Best Tallow Cream
  - For Eczema
- **For Moms**
  - Non-Toxic Skincare
  - Pregnancy-Safe
  - Seed Oil-Free
  - Clean Skincare for Moms
- **Journal** (existing blog link)

4. Click **Save menu**
5. Preview your site — confirm the new items render in the header nav
6. Ping me when done and I'll run the post-nav link-audit (more internal-linking signal = better for rankings)

## Alternative: grant the scope

If you want me to handle menu updates via API going forward, go to **Apps → Develop apps → (your custom app) → Configuration → Admin API scopes** and enable `write_online_store_navigation`. Regenerate the token and share.

For now, the 15 collection pages + 9 articles are all in the Shopify sitemap regardless of nav — Google will find them. The nav update is about **user discovery**, not indexing.
