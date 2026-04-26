# Homestead Fanatic — Homepage Redesign Spec

**Date:** 2026-04-25
**Site:** homesteadfanatic.com
**Target:** WordPress page ID 8 (`/`)
**Approach:** Editorial rebuild on existing GeneratePress theme — no theme swap, no shell access required. New content pushed via WP REST API; CSS injected via theme customizer / Custom CSS.

---

## Visual System

| Property | Value |
|----------|-------|
| Background | `#FAF7F2` (warm off-white) |
| Body text | `#1F1F1B` (deep charcoal) |
| Headline color | `#1F1F1B` |
| Brand accent | `#3F5D45` (muted forest green) — CTAs, links, eyebrow tags |
| Secondary accent | `#D4A574` (warm tan) — dividers, soft bands |
| Border / divider | `#E8E1D5` (warm taupe) |
| Headline font | `Lora`, serif (Google Fonts) |
| Body font | `Inter`, sans-serif (Google Fonts), fall back to system-ui |
| Section padding | 80px vertical desktop / 48px vertical mobile |
| Container max-width | 1200px (with 32px side padding) |
| Type scale | H1 48px / H2 32px / H3 24px / body 17px / line-height 1.7 |
| Card radius | 8px |
| Card shadow | `0 2px 8px rgba(31,31,27,0.06)` (subtle) |

All styles namespaced under `.hf-home-*` to avoid conflict with existing site CSS.

---

## Section Map

### 1. Hero
- **Layout:** 2-column flex, 60/40 left/right on desktop, stacked on mobile
- **Left column:**
  - Eyebrow text: "Practical Self-Reliance"
  - H1 (Lora, 48px): *"Real homesteading. From a mom who learned the hard way."*
  - Subhead: 2 lines combining byline + value prop
  - 2 CTAs: primary green "Start Here" → `/homesteading-skills-beginners/`, outlined "Read My Story" → `/about-2/`
- **Right column:** Sarah Kate portrait. Use existing media library `sarah-kate-wilder.jpg`. Circular crop (border-radius 50%), max width 400px.

### 2. Featured Pillar Story
- **Layout:** Single full-width card, image-left/copy-right on desktop, stacked on mobile
- **Source:** Hardcoded link to `/homesteading-skills-beginners/` (most-evergreen pillar)
- **Components:** Featured image (use post's existing featured image), eyebrow "Pillar Guide", H2 post title, 2-line excerpt, text link "Read the guide →"

### 3. Browse by Topic
- **Layout:** CSS grid, 3×2 desktop, 2×3 tablet, 1-column mobile
- **6 category tiles:** Survival & Prepping (21), Off-Grid Living (17), Health & Wellness (16), Homesteading Tools (12), Emergency Food (10), Food Preservation (8)
- **Each tile:** Photo background (use a representative post's featured image as a background-image), dark gradient overlay (linear-gradient 0deg, rgba(0,0,0,0.6), rgba(0,0,0,0.1)), H3 white serif title bottom-left, post-count badge top-right, full-tile clickable link to category archive
- **Tile aspect ratio:** 4:3
- **Hover:** image scales 1.04, transition 0.3s

### 4. Author Block
- **Layout:** 2-column, photo 33% / copy 67% on desktop, stacked mobile
- **Left:** Circular portrait of Sarah Kate (border-radius 50%, max 280px)
- **Right:**
  - Eyebrow "About the Author"
  - H2: *"Meet Sarah Kate."*
  - Condensed bio (~80 words): hooks on the ice-storm origin
  - 4 E-E-A-T stat chips in a row: *12 acres • 83 articles • 5 years homesteading • Mom of 3*
  - Text link "Read my full story →" → `/about-2/`

### 5. Health Hub Callout (GLP-3)
- **Layout:** Full-width band, forest green background `#3F5D45`, white text
- **Components:**
  - Eyebrow "Health Hub"
  - H2: *"The Natural Health Hub."*
  - Paragraph: 60-word framing — Ozempic price quote → natural research story
  - 3 mini-cards in a row: GLP-3 Pillar Guide, GLP Three Review, Where to Buy. Each card has small icon/eyebrow, H3 title, "Read →" link. White cards with charcoal text on the green band.
- **CTA:** Primary tan-on-charcoal button "Read the GLP-3 Guide" → pillar URL

### 6. Latest Gear & Reviews
- **Layout:** 3-up card grid
- **Source:** Auto-pull 3 most recent published posts in categories `Homesteading Tools` (17) OR `Survival & Prepping` (9). Use `?categories=17,9&orderby=date&per_page=3` style approach.
- **Card:** Featured image (16:9), eyebrow "Gear Review", H3 (Lora, 22px), 1-line excerpt (~120 chars), "Read review →" link
- **Static rendering:** Generate the HTML server-side once at deploy time using REST API; do not require runtime AJAX.

### 7. Latest Posts
- **Layout:** 3-up card grid, same card spec as section 6
- **Source:** 3 most recent published posts overall, excluding any in section 6 to avoid dupes
- **Card eyebrow:** category name of the post (first category)

### 8. Newsletter + Disclosure Footer
- **Layout:** Full-width band, soft tan background `#F4E9D7` (10% tint of `#D4A574` over base), centered content max 720px
- **Headline:** *"Get the homestead playbook."*
- **1-line value prop:** "Practical guides, gear reviews, and stories from the homestead. No spam, ever."
- **Form:**
  - Single email input + green "Subscribe" button
  - Posts to LeadConnector / GoHighLevel webhook (existing on site — use the form embed snippet from the LeadConnector plugin, or post directly to LC's form endpoint)
  - On submit: redirect to a thank-you anchor or show success message inline
- **Below form:** Small muted disclosure line: *"Homestead Fanatic earns commission on some recommended products. Editorial picks come first."* with link to `/affiliate-disclosure/`

---

## Implementation

### Asset prep
- **Hero photo:** use existing `sarah-kate-wilder.jpg` from media library (id known to site)
- **Topic tile images:** pick 6 representative AI-generated featured images already in the media library — one per category, sourced from the hub-and-spoke posts
- **Pillar story image:** featured image of post `homesteading-skills-beginners` (already exists)

### Deployment steps
1. Save current homepage content via REST API (`GET /wp/v2/pages/8`) to a local backup file before any change. Filename: `homesteadfanatic-homepage-backup-2026-04-25.html`
2. Build complete HTML for new homepage as one `<div class="hf-home">` block. Inline-link to the section CSS (or push CSS via Customizer in step 4).
3. Generate dynamic content for sections 6 & 7 by querying WP REST API at deploy time, then bake the resulting HTML into the page content (no runtime data fetch).
4. Push CSS to theme via Customizer (Appearance → Customize → Additional CSS) — single block, namespaced.
5. `POST /wp/v2/pages/8` with new content. Page template stays `full-width-container`.
6. Verify: load homepage, click each link, test mobile breakpoints (375px / 768px / 1200px), verify form submits to LeadConnector.
7. If a section goes wrong, revert by re-pushing the backup content via REST API.

### LeadConnector wire-up
- Inspect existing LeadConnector plugin output on the site for an embedded form ID or webhook URL.
- Use that endpoint as the form `action`. Style our own form HTML around it; don't use LC's auto-generated styling.
- If we can't extract the existing endpoint, fall back to a `<form>` that POSTs to LC's standard form-submit URL with project credentials (which can be retrieved via the LC plugin settings page in wp-admin).

### What's explicitly NOT in scope
- No slider, carousel, modal, popup, exit-intent, or auto-playing media
- No sidebar widgets (per user preference)
- No theme change
- No PHP edits, no shell access required
- No ad network integration
- No comments section on the homepage
- No homepage schema markup beyond what Yoast already adds (handle in a follow-up if needed)

---

## Acceptance Criteria

- Homepage renders cleanly at 375px / 768px / 1024px / 1440px viewport widths.
- All 8 sections present and styled per visual system above.
- All internal links resolve (no 404s).
- LeadConnector form submission produces a contact in LC.
- No console errors.
- Lighthouse desktop performance score ≥ 85 (hero photo lazy-loaded for below-fold images, fonts swap rather than block).
- Backup of original homepage content saved locally before deploy, and revert path documented.

---

## Reversibility

If the result is unloved: re-POST the saved backup to page 8, remove the new CSS block from Customizer. Total revert time < 2 minutes via REST API.

---

## Next-Step Hooks (NOT in this scope)

After homepage ships, the same visual system can be extended to:
- Blog post template (highest revenue lift — separate spec)
- Category archive pages
- Author page

These would each get their own spec.
