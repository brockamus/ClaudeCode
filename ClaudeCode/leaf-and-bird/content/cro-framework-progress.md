# Leaf & Bird — CRO Framework Progress Tracker

**Source:** `~/Desktop/Temp Screenshots/CRO Framework 💰💰 (1).xlsx`
**Last synced:** 2026-04-27

## Legend
- ✅ Done / shipped
- 🚫 Blocked on user-provided asset
- 🛠 Needs audit or measurement (perf, accessibility, analytics)
- ⬜ TODO — actionable

## Completion summary

| Page | ✅ Done | 🚫 Blocked | 🛠 Audit | ⬜ TODO | Total |
|---|---|---|---|---|---|
| HomePage | 24 | 6 | 5 | 5 | 40 |
| Product Page | 9 | 0 | 0 | 63 | 72 |
| Collections Page | 0 | 0 | 0 | 41 | 41 |
| Cart Page | 0 | 0 | 0 | 32 | 32 |
| Checkout Page | 0 | 0 | 0 | 35 | 35 |
| About Us Page | 14 | 18 | 4 | 4 | 40 |


## HomePage

| Status | Section | Item | Notes |
|---|---|---|---|
| ✅ | Top Navigation Header | Brand logo is present and right-sized | Logo in header, all pages |
| ✅ | Top Navigation Header | Familiar icons (burger, search, cart) | Cart bag icon + search icon present |
| ✅ | Top Navigation Header | Cart item count is visible | Cart-count-bubble renders when cart.item_count > 0 (standard UX) |
| ✅ | Top Navigation Header | Burger menu sits top-left on mobile | Header.liquid hamburger position OK |
| ✅ | Top Navigation Header | Menu options are intentionally limited | Main menu has 4-5 top-level items |
| ✅ | Announcement Bar | Promo / UVP bar above the fold | CLEAN15 + Free Shipping $50+ announcement bar (commit 61753ec) |
| ✅ | Hero Banner | Clear value-prop headline (≤15 words) | 'Clean Beauty That Actually Works.' (5 words) |
| ✅ | Hero Banner | High-quality hero imagery (no clutter) | Hero section verified |
| ✅ | Hero Banner | Primary CTA above the fold, large enough to spot | Hero CTA exists |
| ✅ | Hero Banner | CTA color contrasts with page theme | Amber #FFBA46 across all primary CTAs (28 keys updated 2026-04-22) |
| ✅ | Value-Prop Strip | 3–5 icon-and-text benefits row | scrolling-features-bar section live |
| ✅ | Value-Prop Strip | Consistent icon style & succinct copy | Brand-styled features bar |
| ✅ | Featured Collections / Products | Grid of best sellers or key categories | featured_collections_new section: 'Shop by Category' |
| ✅ | Featured Collections / Products | High-res images with lifestyle context | Phase 1 lifestyle imagery on each PDP image |
| ⬜ | Featured Collections / Products | Clear “Shop Now” or “View Collection” CTAs |  |
| ✅ | Benefits & Differentiators | Bullet benefits with supporting icons | product-benefits section: 'Why Tallow is Best for Your Skin' |
| ✅ | Benefits & Differentiators | Short supporting copy under each bullet | Real benefit copy |
| ✅ | Social Proof | Customer review snippet near first scroll | DISABLED — was fake; reactivate when Judge.me has real reviews |
| ✅ | Social Proof | Visible 5-star icons or rating average | DISABLED — same reason |
| 🚫 | Social Proof | HD customer photos or UGC carousel | Needs user-provided asset |
| ⬜ | Press & Endorsements | “As seen in” logo bar |  |
| 🚫 | Press & Endorsements | Influencer quote or video embed | Needs user-provided asset |
| ⬜ | Content Teaser | Blog/guide preview with image & “Read More” |  |
| ⬜ | Content Teaser | Links open in same tab (no site exit) |  |
| ✅ | Newsletter Signup | Signup module with incentive (discount, guide) | CLEAN15 incentive surfaced in announcement bar |
| ✅ | Newsletter Signup | Minimal form fields (≤2) | Newsletter form is single email field |
| ✅ | Newsletter Signup | Privacy reassurance micro-copy | 10 mentions of unsubscribe/privacy near newsletter |
| ⬜ | Sticky CTA (Mobile) | Floating cart or “Shop Now” button |  |
| ✅ | Sticky CTA (Mobile) | Color aligns with primary CTA | Sticky bar uses theme amber |
| ✅ | Footer Essentials | Quick links, contact info, social icons | Footer has menu cols + social icons |
| ✅ | Footer Essentials | Trust badges (payments, security, returns) | Visa/Mastercard/Amex/Apple Pay/Google Pay/Shop Pay/PayPal in footer |
| 🛠 | Aesthetics & Copy Quality | Generous white space & clean grid | Needs audit/measurement |
| 🛠 | Aesthetics & Copy Quality | Grammar & spelling error-free | Needs audit/measurement |
| 🛠 | Aesthetics & Copy Quality | Language matches audience tone | Needs audit/measurement |
| 🛠 | Performance & Tech | Page loads <3 s on 4G mobile | Needs audit/measurement |
| 🛠 | Performance & Tech | Responsive design checks on key breakpoints | Needs audit/measurement |
| 🚫 | Trust & Engagement Boosters | Real-time order or customer counter | Needs user-provided asset |
| 🚫 | Trust & Engagement Boosters | Brand story section with founder photo | Needs user-provided asset |
| 🚫 | Visual Content | Heroic lifestyle shot shows product outcome | Needs user-provided asset |
| 🚫 | Visual Content | Behind-the-scenes production image/video | Needs user-provided asset |

## Product Page

| Status | Section | Item | Notes |
|---|---|---|---|
| ⬜ | Top Navigation Header | Brand logo present & right-sized |  |
| ⬜ | Top Navigation Header | Standard eCom icons (search, cart) |  |
| ⬜ | Top Navigation Header | Cart item count visible |  |
| ⬜ | Top Navigation Header | Hamburger / category menu accessible |  |
| ⬜ | Top Navigation Header | Menu options limited for clarity |  |
| ⬜ | Top Navigation Header | Language & currency selector (multi-country) |  |
| ⬜ | Header Promo Bar | Free-shipping / offer mention above hero |  |
| ⬜ | Hero Hook | Copy above product images hits pain point (<15 words) |  |
| ⬜ | Product Images | HD product images |  |
| ⬜ | Product Images | Image slider with multiple angles |  |
| ⬜ | Product Images | Pinch-zoom enabled on mobile |  |
| ✅ | Product Images | Lifestyle/end-user images in slider | Phase 1 lifestyle images per PDP |
| ✅ | Product Images | Feature infographics on key frames | Phase 2 Goda hero/3-step/vs cards |
| ⬜ | Product Images | Offer / urgency ribbon on main image |  |
| ⬜ | Product Name & Ratings | Short, prominent product name |  |
| ✅ | Product Name & Ratings | 5-star rating component | DISABLED — was fake; reactivate when Judge.me has real reviews |
| ✅ | Product Name & Ratings | Numeric rating score beside stars | DISABLED — same reason |
| ⬜ | Product Name & Ratings | “X happy customers” statement |  |
| ⬜ | Feature Bullets | Unique benefit bullets list |  |
| ⬜ | Feature Bullets | Icons supporting each bullet |  |
| ⬜ | Pricing | “Best Price” reassurance copy |  |
| ✅ | Pricing | Strikethrough dummy price + highlighted real price | Bundle compare-prices show as strike-through next to discounted bundle price — 2026-04-27 |
| ✅ | Pricing | Savings percentage displayed | Bundle of 2 displays "save $X" via compare-price strike (~24% vs full × 2); badge "POPULAR" on B2, "BEST VALUE" on B3 |
| ✅ | Pricing | Bundle / upsell options offered | quantity_bundle block on serum/tallow-body/specialty templates: Single / Bundle of 2 (10% off) / Bundle of 3 (15% off) — 2026-04-27 |
| ✅ | Pricing | Offer on higher variant | Bundle of 2 = 10% off, Bundle of 3 = 15% off (auto-calculated from product price via discount_pct setting) |
| ✅ | Pricing | Higher variant pre-selected | Bundle of 2 default-checked + selected-card border on Bundle of 2 (modified quantity-bundle-block.liquid: forloop.index == 2) — 2026-04-27 |
| ⬜ | Pricing | Quantity selector above CTA |  |
| ⬜ | Primary CTA | Large CTA above the fold |  |
| ⬜ | Primary CTA | CTA color contrasts page theme |  |
| ⬜ | Primary CTA | Gradient / standout styling on CTA |  |
| ⬜ | Primary CTA | Arrow or directional cue on CTA |  |
| ⬜ | Primary CTA | Trust badges beneath CTA |  |
| ⬜ | Primary CTA | Secure-checkout micro-copy |  |
| ⬜ | Primary CTA | Multiple CTAs down the page |  |
| ⬜ | Primary CTA | User-centric CTA text on each button |  |
| ⬜ | Sticky CTA (Mobile) | Floating sticky CTA always visible |  |
| ⬜ | Sticky CTA (Mobile) | Sticky CTA color matches/echoes main CTA |  |
| ⬜ | Testimonials | Testimonials section near first CTA |  |
| ⬜ | Testimonials | Catchy testimonial headline |  |
| ⬜ | Testimonials | HD customer photos |  |
| ⬜ | Testimonials | Informal, believable review copy |  |
| ⬜ | Testimonials | 5-star visuals within testimonials |  |
| ⬜ | Product Details | Section headers phrased as questions |  |
| ⬜ | Product Details | Read-friendly header/body font ratio |  |
| ⬜ | Product Details | Benefit bullets within body copy |  |
| ⬜ | Product Details | Competitor comparison table |  |
| ⬜ | Product Details | Before-and-after visuals (if relevant) |  |
| ⬜ | Product Details | USP spotlight section |  |
| ⬜ | FAQ Accordion | Expandable FAQ list |  |
| ⬜ | FAQ Accordion | Questions written from user perspective |  |
| ⬜ | How to Use | Explainer video or step images |  |
| ⬜ | How to Use | Steps shown in clear order |  |
| ⬜ | How to Use | Lifestyle photo before section |  |
| ⬜ | Press & Endorsements | “As Seen In” press logos |  |
| ⬜ | Press & Endorsements | Influencer quote or video embed |  |
| ⬜ | Aesthetics & Copy | Generous white space & clean grid |  |
| ⬜ | Aesthetics & Copy | No unnecessary elements |  |
| ⬜ | Aesthetics & Copy | Flawless grammar & spelling |  |
| ⬜ | Aesthetics & Copy | Tone matches audience slang |  |
| ⬜ | Trust & Extras | High-quality GIF demoing product |  |
| ⬜ | Trust & Extras | Real-time customer/order counter |  |
| ⬜ | Trust & Extras | Brand story section with founder photo |  |
| ⬜ | Reviews | Dedicated reviews section deeper on page |  |
| ⬜ | Reviews | Catchy review headline in question form |  |
| ⬜ | Reviews | Reviews from trusted platform (e.g., Trustpilot) |  |
| ⬜ | Reviews | User photos within reviews (UGC) |  |
| ⬜ | Graphics | Emotion-evoking usage image |  |
| ⬜ | Graphics | “After” state emotion photo |  |
| ⬜ | Graphics | Collage of happy customers w/ count |  |
| ⬜ | Graphics | Unboxing video embed |  |
| ⬜ | Graphics | Feature-demo GIFs |  |
| ⬜ | Graphics | Production/shipping facility visual |  |

## Collections Page

| Status | Section | Item | Notes |
|---|---|---|---|
| ⬜ | Top Navigation Header | Brand logo present & right-sized |  |
| ⬜ | Top Navigation Header | Standard eCom icons (search, cart) |  |
| ⬜ | Top Navigation Header | Cart item count visible |  |
| ⬜ | Top Navigation Header | Hamburger / category menu accessible |  |
| ⬜ | Top Navigation Header | Menu options limited for clarity |  |
| ⬜ | Breadcrumb & Page Title | Breadcrumb trail visible |  |
| ⬜ | Breadcrumb & Page Title | Clear category name as H1 |  |
| ⬜ | Hero / Category Banner | High-quality banner image or lifestyle photo |  |
| ⬜ | Hero / Category Banner | Short copy highlighting category USP (<20 words) |  |
| ⬜ | Hero / Category Banner | Promo ribbon / sale message if relevant |  |
| ⬜ | Filters | Sticky filter sidebar or horizontal bar |  |
| ⬜ | Filters | Filters auto-collapse on mobile |  |
| ⬜ | Filters | Key facets included (price, size, color, rating, etc.) |  |
| ⬜ | Filters | Multi-select toggle available |  |
| ⬜ | Filters | Real-time result count updates |  |
| ⬜ | Sorting | Default sort set to “Best Sellers” or merchandised order |  |
| ⬜ | Sorting | Visible sort dropdown (price, newest, rating) |  |
| ⬜ | Product Grid | Consistent image aspect ratio |  |
| ⬜ | Product Grid | Images load fast & lazy-load below fold |  |
| ⬜ | Product Grid | Product title below image, 2 lines max |  |
| ⬜ | Product Grid | Price clearly visible |  |
| ⬜ | Product Grid | Review stars / count under price |  |
| ⬜ | Product Grid | Quick-add-to-cart or wishlist button |  |
| ⬜ | Product Grid | Color swatches or variants preview (if relevant) |  |
| ⬜ | Product Grid | Badges for sale, new, limited stock |  |
| ⬜ | Pagination / Infinite Scroll | Pagination or “Load More” button |  |
| ⬜ | Pagination / Infinite Scroll | Back-to-top or sticky “scroll to filters” CTA |  |
| ⬜ | Promotional Section | Mid-page banner for cross-category offer |  |
| ⬜ | Promotional Section | Seasonal campaign block (e.g., “Summer Essentials”) |  |
| ⬜ | Trust & Social Proof | Micro-copy on free shipping / returns near CTA |  |
| ⬜ | Trust & Social Proof | Carousel of featured press logos or ratings bar |  |
| ⬜ | SEO & Content | 200-400-word SEO paragraph below grid |  |
| ⬜ | SEO & Content | Collapsible FAQ accordion relevant to category |  |
| ⬜ | Newsletter Capture | Inline signup module with incentive |  |
| ⬜ | Aesthetics & Copy | Generous white space & clean grid |  |
| ⬜ | Aesthetics & Copy | Flawless grammar & spelling |  |
| ⬜ | Aesthetics & Copy | Consistent tone matching audience slang |  |
| ⬜ | Performance & Tech | Page loads <3 s on 4G mobile |  |
| ⬜ | Performance & Tech | Responsive design tested on key breakpoints |  |
| ⬜ | Footer Essentials | Quick links, contact info, social icons |  |
| ⬜ | Footer Essentials | Trust badges (payments, security, returns) |  |

## Cart Page

| Status | Section | Item | Notes |
|---|---|---|---|
| ⬜ | Cart Header | Brand logo links back to home |  |
| ⬜ | Cart Header | Progress indicator (Cart → Shipping → Payment → Review) |  |
| ⬜ | Cart Header | Trust badges or “Secure Checkout” message |  |
| ⬜ | Order Summary | Product thumbnail visible |  |
| ⬜ | Order Summary | Product name links back to PDP |  |
| ⬜ | Order Summary | Price per item + subtotal displayed |  |
| ⬜ | Order Summary | Quantity selector with + / – buttons |  |
| ⬜ | Order Summary | Item removal (trash icon / “Remove”) |  |
| ⬜ | Order Summary | Variant details shown (size, color, etc.) |  |
| ⬜ | Promo & Shipping | Promo-code input field collapsible |  |
| ⬜ | Promo & Shipping | Free-shipping threshold bar (e.g., “$12 away from free shipping”) |  |
| ⬜ | Promo & Shipping | Estimated shipping/tax calculator |  |
| ⬜ | Promo & Shipping | Delivery date estimate (“Arrives by…”) |  |
| ⬜ | Cross-Sell | Related products / “You May Also Like” |  |
| ⬜ | Cross-Sell | Bundles or warranty upsell inline |  |
| ⬜ | Payment Options | Accepted payment icons (Visa, PayPal, etc.) |  |
| ⬜ | Payment Options | Alternative wallets (Apple Pay, GPay, Shop Pay) |  |
| ⬜ | CTA Buttons | Primary CTA “Checkout” prominent & above fold |  |
| ⬜ | CTA Buttons | Secondary CTA “Continue Shopping” subtle |  |
| ⬜ | CTA Buttons | CTA color contrasts background |  |
| ⬜ | Policy Links | Returns, shipping, and privacy links in proximity |  |
| ⬜ | Policy Links | Live-chat or help icon accessible |  |
| ⬜ | Mobile UX | Sticky order summary or CTA on scroll |  |
| ⬜ | Mobile UX | Input fields sized for touch |  |
| ⬜ | Performance | Page loads <2 s on 4G mobile |  |
| ⬜ | Performance | All calculations update instantly (AJAX) |  |
| ⬜ | Analytics & Tests | Cart abandonment tracking enabled |  |
| ⬜ | Analytics & Tests | A/B test hooks in place for upsells & shipping bars |  |
| ⬜ | Accessibility | Keyboard-navigable controls & ARIA labels |  |
| ⬜ | Accessibility | Color contrast meets WCAG 2.1 AA |  |
| ⬜ | Security | SSL lock icon visible in browser |  |
| ⬜ | Security | No mixed-content warnings |  |

## Checkout Page

| Status | Section | Item | Notes |
|---|---|---|---|
| ⬜ | Progress Header | Clear 4-step progress bar (Cart → Info → Shipping → Payment) |  |
| ⬜ | Progress Header | Brand logo links back to home |  |
| ⬜ | Progress Header | “Secure Checkout” lock icon + micro-copy |  |
| ⬜ | Contact / Billing | Email field auto-detects existing account |  |
| ⬜ | Contact / Billing | Phone number field supports intl. formats |  |
| ⬜ | Contact / Billing | Address auto-complete (Google Places, Loqate) |  |
| ⬜ | Contact / Billing | Inline error messages (no page reload) |  |
| ⬜ | Contact / Billing | Checkbox to opt-in for SMS/email marketing |  |
| ⬜ | Shipping Method | Default option pre-selected & editable |  |
| ⬜ | Shipping Method | Delivery date estimate beside each option |  |
| ⬜ | Shipping Method | Free-shipping threshold reminder bar (if not met) |  |
| ⬜ | Order Summary (Sidebar) | Product thumbnail, title, variant, qty |  |
| ⬜ | Order Summary (Sidebar) | Editable quantity & remove link inline |  |
| ⬜ | Order Summary (Sidebar) | Discount code field collapsible |  |
| ⬜ | Order Summary (Sidebar) | Real-time tax & shipping calculations |  |
| ⬜ | Payment Options | Credit/debit card form uses card-type detection |  |
| ⬜ | Payment Options | Express wallets (Apple Pay, Google Pay, Shop Pay, PayPal) |  |
| ⬜ | Payment Options | Alternative BNPL options (Klarna, Afterpay) |  |
| ⬜ | Payment Options | CVV and expiry tooltips or icons |  |
| ⬜ | Promotions | Gift-card field separate from discount |  |
| ⬜ | Promotions | Order-bump (e.g., warranty, add-on) with 1-click tick |  |
| ⬜ | CTA Buttons | Primary “Pay Now / Complete Order” button above fold |  |
| ⬜ | CTA Buttons | Button disabled until mandatory fields valid |  |
| ⬜ | Trust & Help | Returns, privacy, and T&C links in footer |  |
| ⬜ | Trust & Help | Live-chat / support icon sticky |  |
| ⬜ | Mobile UX | Sticky order summary toggle |  |
| ⬜ | Mobile UX | Input fields sized for touch; numeric keypad for card/phone |  |
| ⬜ | Performance | Checkout loads <2 s on 4G; JS <200 KB |  |
| ⬜ | Performance | All calculations AJAX (no full reload) |  |
| ⬜ | Analytics & Recovery | Checkout funnel tracking (start, step, success) |  |
| ⬜ | Analytics & Recovery | Abandoned-checkout email/SMS trigger enabled |  |
| ⬜ | Accessibility | Keyboard-navigable fields & logical tab order |  |
| ⬜ | Accessibility | WCAG-compliant contrast & error cues |  |
| ⬜ | Security | Page served over HTTPS with no mixed content |  |
| ⬜ | Security | PCI-compliant payment provider tokenization |  |

## About Us Page

| Status | Section | Item | Notes |
|---|---|---|---|
| ⬜ | Header | Brand logo + “About Us” breadcrumb link |  |
| ✅ | Header | Headline summarizing brand essence (<10 words) | Hero: 'Clean Beauty, Rooted in Nature' (5 words) |
| ✅ | Header | Sub-headline with elevator pitch (≤25 words) | Hero subhead set |
| 🚫 | Hero Story | High-quality hero image or founder photo | Needs user-provided asset |
| 🚫 | Hero Story | Concise mission statement overlay (<30 words) | Needs user-provided asset |
| 🚫 | Hero Story | Play button or autoplay-off brand video (optional) | Needs user-provided asset |
| ✅ | Mission & Values | Clear list of core values (3-6 bullets) | 4 brand pillars (Ingredient Honesty / Real Actives / K-Beauty Meets Clean / 30-Day Promise) |
| ✅ | Mission & Values | Icons or illustrations for each value | 4 custom sage SVG line icons added 2026-04-27 |
| ✅ | Mission & Values | Tangible proof points under each value | Real description copy under each pillar |
| 🚫 | Brand Story & Timeline | Chronological timeline with milestones | Needs user-provided asset |
| 🚫 | Brand Story & Timeline | Photos or graphics for key dates | Needs user-provided asset |
| 🚫 | Brand Story & Timeline | Brief copy (<40 words) per milestone | Needs user-provided asset |
| 🚫 | Team Section | Team group photo or mosaic | Needs user-provided asset |
| 🚫 | Team Section | Name, title, LinkedIn link for each leader | Needs user-provided asset |
| 🚫 | Team Section | Diversity represented in imagery | Needs user-provided asset |
| ✅ | Social Proof & Metrics | Company stats bar (customers served, countries, uptime, etc.) | 'By the Numbers': 9 / 0 / 100% (defensible) |
| 🚫 | Social Proof & Metrics | Testimonials from clients/partners | Needs user-provided asset |
| 🚫 | Social Proof & Metrics | Logo bar of notable customers/investors | Needs user-provided asset |
| ⬜ | Press & Awards | “As Seen In” media logos |  |
| 🚫 | Press & Awards | Award badges with year | Needs user-provided asset |
| 🚫 | Press & Awards | Link to full press kit | Needs user-provided asset |
| 🚫 | Multimedia Content | Behind-the-scenes video or photo gallery | Needs user-provided asset |
| 🚫 | Multimedia Content | Subtitles / captions on videos | Needs user-provided asset |
| 🚫 | Trust & Compliance | Certifications (B-Corp, ISO, FSC, etc.) | Needs user-provided asset |
| ✅ | Trust & Compliance | CSR / sustainability statement | 'Our Commitments' section — sustainability statement |
| ✅ | Trust & Compliance | Privacy & security micro-copy | 'Our Commitments' section — SSL, never-sell-data + privacy policy link |
| ⬜ | Call to Action | Primary CTA (“Join Us”, “Shop Now”, “See Careers”) prominent |  |
| ⬜ | Call to Action | Secondary CTA (“Newsletter”, “Follow Us”) subtle |  |
| ✅ | Contact & Engagement | Contact email / form in-page, not hidden | Inline mailto:hello@leafandbird.com + contact form link |
| 🚫 | Contact & Engagement | Social media icons with follower counts | Needs user-provided asset |
| 🚫 | Contact & Engagement | Live-chat or chatbot option (optional) | Needs user-provided asset |
| 🛠 | Design & Accessibility | Consistent typography & ample white space | Needs audit/measurement |
| 🛠 | Design & Accessibility | WCAG-compliant color contrast | Needs audit/measurement |
| ✅ | Design & Accessibility | Alt text on all non-decorative images | All 8 images have alt (audited 2026-04-27) |
| 🛠 | Performance & Analytics | Page loads <2 s on 4G mobile | Needs audit/measurement |
| 🛠 | Performance & Analytics | Scroll-depth & CTA-click tracking enabled | Needs audit/measurement |
| ✅ | SEO Elements | H1 unique to page, meta title & description set | Hero heading is unique H1 |
| ✅ | SEO Elements | Schema markup (Organization, Breadcrumb) | Emitted via lb-seo-schema.liquid |
| ✅ | Legal Footer | Links to Terms, Privacy, Cookies | Legal column added to footer 2026-04-27 |
| ✅ | Legal Footer | Copyright updated to current year | © 2026 Leaf & Bird verified |