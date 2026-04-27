# Homestead Fanatic × Leaf & Bird — 10 Article Batch — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship 10 cornerstone natural-skincare articles on homesteadfanatic.com featuring leafandbird.com products as recommendations, in Sarah Kate Wilder's voice, with proper FTC ownership disclosure.

**Architecture:** Each article is authored as a single self-contained HTML body + metadata JSON in `/Users/skitch/hf-leafbird-articles/`. Featured images generated via Gemini Imagen 4.0 and uploaded to WP media. Articles published via WordPress REST API to homesteadfanatic.com (category 18, Health & Wellness). All cross-domain links to leafandbird.com use stable Shopify product handles. Manifest tracks every published post for one-shot revert.

**Tech Stack:** WordPress REST API (`wp/v2`), Yoast meta REST, Gemini API (Imagen 4.0), Python 3 stdlib (urllib + json), HTML/CSS only — no JS, no framework.

**Spec reference:** `/Users/skitch/homesteadfanatic-leafbird-articles-spec.md`

**Working directory:** `/Users/skitch/hf-leafbird-articles/` (created at Task 0)

**Credentials in env-style for tasks:**
```
WP_USER=fred
WP_PASS="Md7C 1cWk yhcX jmfs ffin lrZ6"
WP_BASE=https://homesteadfanatic.com/wp-json/wp/v2
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
HF_BLOG_CATEGORY_ID=18  # Health & Wellness
```

**Gemini API key:** stored at `~/.claude/projects/-Users-skitch/memory/reference_gemini_api.md` (per project memory). Image generation script reuse: `/Users/skitch/ClaudeCode/leaf-and-bird/scripts/gen_image.py` (proven on prior 13 L&B articles).

---

## File Structure

```
/Users/skitch/hf-leafbird-articles/
  manifest.json                       # rolling: { articles: [{slug,id,link,...}] }
  shared/
    disclosure-block.html             # canonical FTC disclosure HTML
    voice-guide.md                    # Sarah Kate voice rules + tone examples
    article-template.html             # full HTML scaffold (hero, disclosure slot, body slot, footer)
    style.css                         # branded styles incl. .hf-disclosure
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
    01-{slug}.json … 10-{slug}.json   # title_tag, meta_desc, FAQ JSON-LD
  images/
    01-{slug}.jpg … 10-{slug}.jpg     # 1200×630 featured images
  REVERT.sh                           # idempotent unpublish-all script
```

---

## Canonical FTC Disclosure HTML (used in every article)

```html
<div class="hf-disclosure" style="background:#F4E9D7;border-left:4px solid #3F5D45;padding:16px 22px;margin:24px 0;font-size:14px;line-height:1.6;font-style:italic;color:#1F1F1B;">
  <strong>Disclosure:</strong> I co-own Leaf &amp; Bird, the skincare brand featured in this post. My recommendations reflect my honest experience with the products and the reasoning behind why I started the brand in the first place. Other products mentioned (drugstore comparisons, ingredient references) are linked for context only. <a href="https://homesteadfanatic.com/affiliate-disclosure/" style="color:#3F5D45;">Read the full disclosure</a>.
</div>
```

This block is inlined in every article so it works regardless of theme CSS state. Wording is verbatim and **must not be softened**.

---

## Sarah Kate Voice Rules (referenced by every article task)

- **First person** ("I tried", "I switched", "what I noticed")
- **Lived-experience anchors**: 12-acre Texas homestead outside Wimberley; mom of 3; started homesteading after 2021 ice storm; Costco-membership-suburban-mom past
- **Voice tone**: practical, non-gatekeepy, occasional honest mistakes ("I killed my first garden")
- **Pregnancy / postpartum / perimenopause** are real life-stages she's referenced; OK to mention naturally; do NOT invent a current pregnancy
- **Never claim**: medical credentials, specific lab tests, dermatologist consultations, FDA approvals
- **Brand mentions**: Refer to "Leaf & Bird" by name. Use product names exactly as on leafandbird.com.
- **Phrasing safety**: Default to "I've been testing", "I switched to", "in my routine right now". Avoid hard duration claims ("for 5 years") unless agreed upfront.

---

## Standard Article Structure (every article uses this skeleton)

```html
<style>
  .hf-art { font-family: 'Inter', system-ui, sans-serif; font-size: 17px; line-height: 1.7; color: #1F1F1B; max-width: 800px; margin: 0 auto; padding: 0 20px; }
  .hf-art h1, .hf-art h2, .hf-art h3 { font-family: 'Lora', Georgia, serif; line-height: 1.25; color: #1F1F1B; }
  .hf-art h1 { font-size: 40px; margin: 0 0 8px; }
  .hf-art h2 { font-size: 28px; margin: 40px 0 14px; }
  .hf-art h3 { font-size: 22px; margin: 28px 0 10px; }
  .hf-art .hero { background: linear-gradient(135deg, #3F5D45 0%, #2F4733 100%); color: #fff; padding: 56px 36px; border-radius: 8px; margin-bottom: 24px; }
  .hf-art .hero h1 { color: #fff; }
  .hf-art .hero .byline { font-size: 14px; opacity: 0.85; margin-top: 12px; }
  .hf-art .tldr { background: #F4E9D7; border-left: 4px solid #D4A574; padding: 16px 22px; margin: 24px 0; font-size: 16px; }
  .hf-art .tldr strong { color: #2F4733; }
  .hf-art .product-card { background: #fff; border: 1px solid #E8E1D5; border-radius: 8px; padding: 22px; margin: 28px 0; display: flex; gap: 20px; align-items: center; }
  .hf-art .product-card img { width: 110px; height: 110px; object-fit: cover; border-radius: 6px; }
  .hf-art .product-card a.cta { display: inline-block; margin-top: 8px; background: #3F5D45; color: #fff; padding: 10px 18px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 14px; }
  .hf-art .faq dt { font-weight: 600; margin-top: 16px; color: #2F4733; }
  .hf-art .faq dd { margin: 6px 0 0 0; }
</style>

<div class="hf-art">
  <header class="hero">
    <h1>{{TITLE}}</h1>
    <p class="byline">By Sarah Kate Wilder</p>
  </header>

  <!-- FTC disclosure block -->
  <div class="hf-disclosure" …>{{DISCLOSURE}}</div>

  <!-- TL;DR -->
  <div class="tldr"><strong>The short version:</strong> {{TLDR_TEXT}}</div>

  <!-- INTRO PARA -->
  <p>{{INTRO}}</p>

  <!-- BODY: H2s + paragraphs + product card mid-article -->

  <!-- FAQ -->
  <h2>Frequently Asked Questions</h2>
  <dl class="faq">
    <dt>Q1?</dt><dd>A1.</dd>
    …
  </dl>

  <!-- FOOTER CTA / SIBLING LINK -->
</div>
```

---

## Task 0: Set up working directory + shared assets

**Files:**
- Create: `/Users/skitch/hf-leafbird-articles/manifest.json`
- Create: `/Users/skitch/hf-leafbird-articles/shared/disclosure-block.html`
- Create: `/Users/skitch/hf-leafbird-articles/shared/voice-guide.md`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p /Users/skitch/hf-leafbird-articles/{shared,drafts,meta,images}
```

- [ ] **Step 2: Initialize manifest**

```bash
echo '{"date":"2026-04-26","articles":[]}' > /Users/skitch/hf-leafbird-articles/manifest.json
```

- [ ] **Step 3: Write shared FTC disclosure block** (copy verbatim from this plan's Canonical Disclosure section above)

```bash
cat > /Users/skitch/hf-leafbird-articles/shared/disclosure-block.html <<'HTML'
<div class="hf-disclosure" style="background:#F4E9D7;border-left:4px solid #3F5D45;padding:16px 22px;margin:24px 0;font-size:14px;line-height:1.6;font-style:italic;color:#1F1F1B;">
  <strong>Disclosure:</strong> I co-own Leaf &amp; Bird, the skincare brand featured in this post. My recommendations reflect my honest experience with the products and the reasoning behind why I started the brand in the first place. Other products mentioned (drugstore comparisons, ingredient references) are linked for context only. <a href="https://homesteadfanatic.com/affiliate-disclosure/" style="color:#3F5D45;">Read the full disclosure</a>.
</div>
HTML
```

- [ ] **Step 4: Write voice guide for subagents**

Save the Sarah Kate Voice Rules section above to `/Users/skitch/hf-leafbird-articles/shared/voice-guide.md`. Subagents reference it before writing any article body.

```bash
cat > /Users/skitch/hf-leafbird-articles/shared/voice-guide.md <<'EOF'
# Sarah Kate Wilder Voice Rules

- First person: "I tried", "I switched", "what I noticed"
- Anchors: 12-acre Texas homestead outside Wimberley; mom of 3; 2021 ice-storm origin; Costco-mom past
- Tone: practical, non-gatekeepy, honest mistakes ("I killed my first garden")
- Pregnancy / postpartum / perimenopause: OK to reference past or general; do NOT invent a current pregnancy
- Never claim: medical credentials, lab tests, dermatologist consults, FDA approvals
- Brand: refer to "Leaf & Bird" by name; product names exactly as on leafandbird.com
- Phrasing safety: "I've been testing", "I switched to", "in my routine right now"; avoid hard duration claims unless agreed
EOF
```

- [ ] **Step 5: Verify**

```bash
ls -la /Users/skitch/hf-leafbird-articles/shared/
test -s /Users/skitch/hf-leafbird-articles/manifest.json && echo "manifest ok"
```

Expected: 2 shared files present, manifest non-empty.

---

## Task 1: Pull L&B product references + write helper publish script

**Files:**
- Create: `/Users/skitch/hf-leafbird-articles/shared/lb-products.json`
- Create: `/Users/skitch/hf-leafbird-articles/shared/publish_article.py`

**Why:** Each article will link to specific L&B product URLs. Pulling the canonical product page URLs and product images once avoids ten subagents each making redundant calls.

- [ ] **Step 1: Use Shopify Storefront (no auth needed for public product data)**

```bash
python3 - <<'PY'
import urllib.request, json
products = [
    "peptide-eye-gel-cream",
    "pdrn-brightening-serum",
    "tallow-cream-lemongrass-lavender",
    "tallow-cream-orange-bergamot",
    "tallow-cream-peaceful-night",
]
out = {}
for handle in products:
    url = f"https://leafandbird.com/products/{handle}.json"
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    d = json.loads(urllib.request.urlopen(req).read())["product"]
    out[handle] = {
        "url": f"https://leafandbird.com/products/{handle}",
        "title": d["title"],
        "image": d["images"][0]["src"] if d.get("images") else None,
        "price": d["variants"][0]["price"] if d.get("variants") else None,
    }
import json as J
J.dump(out, open('/Users/skitch/hf-leafbird-articles/shared/lb-products.json','w'), indent=2)
print(J.dumps(out, indent=2))
PY
```

- [ ] **Step 2: Verify all 5 products have image + URL**

```bash
python3 -c "
import json
d = json.load(open('/Users/skitch/hf-leafbird-articles/shared/lb-products.json'))
for h,p in d.items():
    assert p['url'], h
    assert p['image'], f'no image for {h}'
    assert p['price'], f'no price for {h}'
print('all 5 products resolved')
"
```

Expected: `all 5 products resolved`.

- [ ] **Step 3: Write helper `publish_article.py`** that handles the mechanical steps (image upload, post create, manifest append, verification). Article tasks below call this helper with per-article args.

```bash
cat > /Users/skitch/hf-leafbird-articles/shared/publish_article.py <<'PY'
"""HF × L&B article publisher. Used by article tasks. Each article task
provides: slug, title, focus_kw, body HTML path, meta JSON path, image path.
This script: uploads image to WP media (sets alt), POSTs the article via WP REST,
appends to manifest, and verifies the live URL contains the FTC disclosure +
at least one leafandbird.com link.
"""
import argparse, base64, json, pathlib, re, sys, time, urllib.request

WP_USER = "fred"
WP_PASS = "Md7C 1cWk yhcX jmfs ffin lrZ6"
WP_BASE = "https://homesteadfanatic.com/wp-json/wp/v2"
UA      = "Mozilla/5.0 (Macintosh)"
HF_CAT  = 18  # Health & Wellness
ROOT    = pathlib.Path("/Users/skitch/hf-leafbird-articles")
MANIFEST = ROOT / "manifest.json"
AUTH    = base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()

def req(path, *, method="GET", payload=None, raw=None, ctype="application/json", extra=None):
    url = path if path.startswith("http") else f"{WP_BASE}{path}"
    data = raw if raw is not None else (json.dumps(payload).encode() if payload else None)
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header("Authorization", f"Basic {AUTH}")
    r.add_header("User-Agent", UA)
    if data is not None: r.add_header("Content-Type", ctype)
    if extra:
        for k,v in extra.items(): r.add_header(k, v)
    return json.loads(urllib.request.urlopen(r, timeout=60).read())

def upload_image(image_path, slug, alt_text):
    body = pathlib.Path(image_path).read_bytes()
    fname = f"{slug}.jpg"
    media = req("/media", method="POST", raw=body, ctype="image/jpeg",
                extra={"Content-Disposition": f'attachment; filename="{fname}"'})
    # set alt text via update
    req(f"/media/{media['id']}", method="POST", payload={"alt_text": alt_text})
    return media["id"], media["source_url"]

def publish(slug, title, focus_kw, body_path, meta_path, image_path):
    body = pathlib.Path(body_path).read_text(encoding="utf-8")
    meta = json.loads(pathlib.Path(meta_path).read_text(encoding="utf-8"))
    media_id, media_url = upload_image(image_path, slug, meta["image_alt"])
    faq_script = "\n<script type=\"application/ld+json\">" + json.dumps(meta["faq_jsonld"]) + "</script>\n"
    payload = {
        "title": title, "slug": slug, "content": body + faq_script,
        "status": "publish", "categories": [HF_CAT], "featured_media": media_id,
        "meta": {
            "_yoast_wpseo_title": meta["title_tag"],
            "_yoast_wpseo_metadesc": meta["meta_desc"],
            "_yoast_wpseo_focuskw": focus_kw,
        },
    }
    result = req("/posts", method="POST", payload=payload)
    # append to manifest
    m = json.loads(MANIFEST.read_text())
    m["articles"].append({
        "slug": slug, "id": result["id"], "link": result["link"],
        "title": title, "modified": result["modified"],
        "featured_media_id": media_id, "featured_media_url": media_url,
    })
    MANIFEST.write_text(json.dumps(m, indent=2))
    print(f"PUBLISHED #{result['id']} {result['link']}")
    return result

def verify(slug):
    m = json.loads(MANIFEST.read_text())
    entry = next((a for a in m["articles"] if a["slug"] == slug), None)
    if not entry: raise SystemExit(f"slug not in manifest: {slug}")
    url = f"{entry['link']}?cb={int(time.time())}"
    r = urllib.request.Request(url, headers={"User-Agent": UA})
    html = urllib.request.urlopen(r, timeout=30).read().decode("utf-8","ignore")
    assert "I co-own Leaf" in html, "FTC disclosure missing in rendered HTML"
    assert "leafandbird.com/products/" in html, "no leafandbird.com product link in rendered HTML"
    h2s = re.findall(r"<h2[^>]*>(.*?)</h2>", html, re.DOTALL|re.IGNORECASE)
    assert len(h2s) >= 5, f"expected ≥5 H2s, found {len(h2s)}"
    print(f"OK {slug} ({len(html)} bytes; {len(h2s)} H2s)")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    pub = sub.add_parser("publish")
    pub.add_argument("--slug", required=True)
    pub.add_argument("--title", required=True)
    pub.add_argument("--focus-kw", required=True)
    pub.add_argument("--body", required=True)
    pub.add_argument("--meta", required=True)
    pub.add_argument("--image", required=True)
    ver = sub.add_parser("verify")
    ver.add_argument("--slug", required=True)
    a = p.parse_args()
    if a.cmd == "publish":
        publish(a.slug, a.title, a.focus_kw, a.body, a.meta, a.image)
    else:
        verify(a.slug)
PY
chmod +x /Users/skitch/hf-leafbird-articles/shared/publish_article.py
```

Verify:
```bash
python3 /Users/skitch/hf-leafbird-articles/shared/publish_article.py --help
```

Expected: argparse usage printed.

---

## Per-Article Task Pattern

Every article task (Tasks 2–11) follows the same 5-step pattern. The pattern is defined once here so each task can stay focused on the article's content + parameters.

**Step A: Generate featured image** (call `gen_image.py` with the article's prompt)

```bash
cd /Users/skitch/ClaudeCode/leaf-and-bird
python3 scripts/gen_image.py \
  --prompt "{{IMAGE_PROMPT}}" \
  --output /Users/skitch/hf-leafbird-articles/images/{{NN}}-{{SLUG}}.jpg \
  --aspect 16:9
# fallback if --aspect unsupported: use --width 1200 --height 630
```

Expected: file > 100KB present at the output path.

**Step B: Write article body HTML** to `/Users/skitch/hf-leafbird-articles/drafts/{{NN}}-{{SLUG}}.html`

Body must include (in order):
1. `<style>` block (paste the canonical block from "Standard Article Structure" section above)
2. Hero `<header class="hero">` with H1 (article title) + byline
3. FTC disclosure block (paste verbatim from `shared/disclosure-block.html`)
4. TL;DR div
5. Intro paragraph (80–150 words)
6. The required H2 sequence (specified per article), each with appropriate body content + at least one transition or anchor sentence per section
7. One inline product card linking to the article's L&B product URL — use the canonical `.product-card` HTML from "Standard Article Structure" with the product image from `shared/lb-products.json`
8. FAQ `<dl class="faq">` section with 4–6 conversational Q&As
9. Footer paragraph linking to the specified sibling articles

After writing, verify:
```bash
python3 - <<PY
import re
body = open('/Users/skitch/hf-leafbird-articles/drafts/{{NN}}-{{SLUG}}.html').read()
text = re.sub(r'<[^>]+>',' ', body)
text = re.sub(r'\s+',' ', text).strip()
words = len(text.split())
target = {{WORD_TARGET}}
assert int(target*0.9) <= words <= int(target*1.1), f"word count {words} outside ±10% of {target}"
assert 'I co-own Leaf' in body, "missing FTC disclosure"
assert '{{LB_PRODUCT_URL}}' in body, "missing required L&B product link"
h2s = re.findall(r'<h2[^>]*>(.*?)</h2>', body, re.DOTALL|re.IGNORECASE)
assert len(h2s) == {{H2_COUNT}}, f"expected {{H2_COUNT}} H2s, got {len(h2s)}"
print(f'body ok: {words} words, {len(h2s)} H2s')
PY
```

**Step C: Write meta JSON** to `/Users/skitch/hf-leafbird-articles/meta/{{NN}}-{{SLUG}}.json`:

```json
{
  "title_tag": "{{TITLE_TAG <= 62 chars}}",
  "meta_desc": "{{META_DESC <= 160 chars}}",
  "image_alt": "{{ALT_TEXT including primary keyword naturally}}",
  "faq_jsonld": {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {"@type":"Question","name":"<Q>","acceptedAnswer":{"@type":"Answer","text":"<A>"}}
    ]
  }
}
```

The Q/A pairs in `faq_jsonld` must mirror the FAQ section of the body HTML 1:1.

**Step D: Publish + verify**

```bash
python3 /Users/skitch/hf-leafbird-articles/shared/publish_article.py publish \
  --slug "{{SLUG}}" \
  --title "{{TITLE}}" \
  --focus-kw "{{FOCUS_KW}}" \
  --body "/Users/skitch/hf-leafbird-articles/drafts/{{NN}}-{{SLUG}}.html" \
  --meta "/Users/skitch/hf-leafbird-articles/meta/{{NN}}-{{SLUG}}.json" \
  --image "/Users/skitch/hf-leafbird-articles/images/{{NN}}-{{SLUG}}.jpg"

python3 /Users/skitch/hf-leafbird-articles/shared/publish_article.py verify --slug "{{SLUG}}"
```

Expected: `PUBLISHED #<id> https://homesteadfanatic.com/{{SLUG}}/` then `OK {{SLUG}} (<bytes>; <h2_count> H2s)`.

---

## Task 2: Article #1 — `vegan-eye-cream-homesteader-review`

**Why:** Cornerstone first-person review for the eye cream cluster. Highest-leverage of the 4 eye-cream articles.

**Files:**
- Create: `/Users/skitch/hf-leafbird-articles/drafts/01-vegan-eye-cream-homesteader-review.html`
- Create: `/Users/skitch/hf-leafbird-articles/meta/01-vegan-eye-cream-homesteader-review.json`
- Create: `/Users/skitch/hf-leafbird-articles/images/01-vegan-eye-cream-homesteader-review.jpg`

**Article spec:**
- Slug: `vegan-eye-cream-homesteader-review`
- Working title: "Why I Switched My Eye Cream — A Crunchy Mom's Honest Review"
- Primary keyword: `vegan eye cream review`
- Word target: 2,200 (±10%)
- L&B product link target: `https://leafandbird.com/products/peptide-eye-gel-cream`
- Required H2 sequence (this article's HCU-diverse layout):
  1. Why I Started Looking for a New Eye Cream
  2. What I Was Using Before (and What Was Wrong With It)
  3. What I Wanted in a Replacement
  4. Why I Ended Up With Leaf & Bird's Peptide Eye Gel-Cream
  5. What 60 Days of Using It Looks Like
  6. Honest Pros and Cons
  7. Frequently Asked Questions
- Internal links (HF):
  - At least 1 link to the existing GLP-3 pillar (https://homesteadfanatic.com/glp3-the-complete-guide-to-natural-weight-management-for-homesteaders/) as a "natural-health journey" cross-cluster bridge
  - At least 1 link to https://homesteadfanatic.com/category/health-wellness/
- Internal links (sibling articles in this slate — published in later tasks; OK to link forward by slug):
  - https://homesteadfanatic.com/peptide-eye-cream-pregnancy-safe/ (article #2)
  - https://homesteadfanatic.com/acetyl-tetrapeptide-5-explained/ (article #4)
- Outbound citation: 1 citation supporting peptide skincare evidence (PubMed / NIH / dermatology research)

**Image prompt** (Gemini Imagen 4.0):
> "Macro photograph of a small green-and-cream skincare jar on a soft white linen background, golden afternoon light filtering through. Rosemary or olive sprig nearby. Clean editorial styling. 1200x630 16:9. No text, no watermarks."

**Parameter substitution for Steps A–D (per the pattern):**
- `{{NN}}` = `01`
- `{{SLUG}}` = `vegan-eye-cream-homesteader-review`
- `{{TITLE}}` = `Why I Switched My Eye Cream — A Crunchy Mom's Honest Review`
- `{{FOCUS_KW}}` = `vegan eye cream review`
- `{{WORD_TARGET}}` = `2200`
- `{{H2_COUNT}}` = `7`
- `{{LB_PRODUCT_URL}}` = `https://leafandbird.com/products/peptide-eye-gel-cream`
- `{{IMAGE_PROMPT}}` = (image prompt above)

Meta JSON to save at `meta/01-vegan-eye-cream-homesteader-review.json`:
```json
{
  "title_tag": "Vegan Eye Cream Review: A Crunchy Mom's Honest Take (2026)",
  "meta_desc": "I switched my eye cream after my third baby. Here's why I picked Leaf & Bird's vegan peptide eye gel-cream — and what 60 days actually looked like.",
  "image_alt": "Vegan peptide eye cream jar on linen — Leaf & Bird vegan eye cream review",
  "faq_jsonld": {
    "@context": "https://schema.org", "@type": "FAQPage",
    "mainEntity": [
      {"@type":"Question","name":"<Q1>","acceptedAnswer":{"@type":"Answer","text":"<A1>"}}
    ]
  }
}
```
*(Q/A pairs in `faq_jsonld` mirror the body's FAQ section 1:1; 4–6 Q&As.)*

- [ ] **Step A: Generate featured image** (per Pattern Step A above)
- [ ] **Step B: Write `drafts/01-vegan-eye-cream-homesteader-review.html`** (per Pattern Step B above; word target 2,200; required H2 sequence above)
- [ ] **Step C: Write `meta/01-vegan-eye-cream-homesteader-review.json`** (per Pattern Step C above; with the meta values above)
- [ ] **Step D: Publish + verify** (per Pattern Step D above)

---

## Task 3: Article #2 — `peptide-eye-cream-pregnancy-safe`

**Why:** Pregnancy-safe angle; high commercial intent; ties to existing HF preparedness/health audience.

**Files:**
- Create: `/Users/skitch/hf-leafbird-articles/drafts/02-peptide-eye-cream-pregnancy-safe.html`
- Create: `/Users/skitch/hf-leafbird-articles/meta/02-peptide-eye-cream-pregnancy-safe.json`
- Create: `/Users/skitch/hf-leafbird-articles/images/02-peptide-eye-cream-pregnancy-safe.jpg`

**Article spec:**
- Slug: `peptide-eye-cream-pregnancy-safe`
- Working title: "Pregnancy-Safe Eye Cream: What I Looked For (and Avoided)"
- Primary keyword: `pregnancy safe eye cream`
- Word target: 1,900 (±10%)
- L&B product link: `https://leafandbird.com/products/peptide-eye-gel-cream`
- Required H2 sequence:
  1. Why Eye Cream Choice Matters in Pregnancy
  2. The Ingredients I Avoided
  3. The Ingredients I Looked For
  4. My Pregnancy-Safe Eye Cream Pick
  5. How to Read an Eye Cream Label (the Sarah-Kate Way)
  6. Frequently Asked Questions
- Internal HF links: article #1 (`vegan-eye-cream-homesteader-review`), article #4 (`acetyl-tetrapeptide-5-explained`), HF crunchy-mom / Health & Wellness category
- Citation required (pregnancy claim): cite at least 1 ACOG / Mayo Clinic / NIH source on retinol-during-pregnancy guidance
- L&B link target: peptide eye gel-cream

**Image prompt:**
> "Soft macro photograph of a green skincare jar on a wooden tray with a sprig of dried lavender, cream-colored linen, soft natural daylight. Cozy nursery vibe without showing a baby. 16:9. No text."

**Parameter substitution:**
- `{{NN}}` = `02` · `{{SLUG}}` = `peptide-eye-cream-pregnancy-safe` · `{{TITLE}}` = `Pregnancy-Safe Eye Cream: What I Looked For (and Avoided)`
- `{{FOCUS_KW}}` = `pregnancy safe eye cream` · `{{WORD_TARGET}}` = `1900` · `{{H2_COUNT}}` = `6`
- `{{LB_PRODUCT_URL}}` = `https://leafandbird.com/products/peptide-eye-gel-cream`

Meta JSON values:
```json
{
  "title_tag": "Pregnancy-Safe Eye Cream: What to Look For (2026)",
  "meta_desc": "Pregnant and need to swap your eye cream? Here's the ingredient checklist I used — what I avoided, what I kept, and the one I picked.",
  "image_alt": "Pregnancy-safe eye cream jar with dried lavender — pregnancy safe eye cream"
}
```

- [ ] **Step A: Generate featured image** (per Pattern Step A above)
- [ ] **Step B: Write `drafts/02-peptide-eye-cream-pregnancy-safe.html`** (per Pattern Step B; word target 1,900; H2 sequence above; include outbound citation to ACOG/Mayo/NIH on retinol-during-pregnancy)
- [ ] **Step C: Write `meta/02-peptide-eye-cream-pregnancy-safe.json`** (per Pattern Step C; with values above; 4–6 Q&As mirroring body FAQ)
- [ ] **Step D: Publish + verify** (per Pattern Step D)

---

## Task 4: Article #3 — `caffeine-free-eye-cream-why`

**Files:**
- Create: drafts/03, meta/03, images/03

**Article spec:**
- Slug: `caffeine-free-eye-cream-why`
- Working title: "Why I Stopped Using Caffeine Eye Cream After My Third Baby"
- Primary keyword: `caffeine free eye cream`
- Word target: 1,700 (±10%)
- L&B link: peptide eye gel-cream (caffeine-free is its USP)
- Required H2 sequence:
  1. Why I Used to Reach for Caffeine Eye Cream
  2. What Caffeine Actually Does Under Your Eyes
  3. Why I Stopped After My Third Baby
  4. What I Use Instead
  5. Who Caffeine-Free Is Right For
  6. Frequently Asked Questions
- Internal HF links: article #1, article #4, Health & Wellness category
- Citation: 1 source on caffeine vasoconstriction or topical caffeine research

**Image prompt:**
> "Top-down macro of a green skincare jar next to an espresso cup turned over (empty) on a textured wooden table — implying 'no more caffeine'. Soft morning light. Editorial styling. 16:9. No text."

**Parameter substitution:**
- `{{NN}}` = `03` · `{{SLUG}}` = `caffeine-free-eye-cream-why` · `{{TITLE}}` = `Why I Stopped Using Caffeine Eye Cream After My Third Baby`
- `{{FOCUS_KW}}` = `caffeine free eye cream` · `{{WORD_TARGET}}` = `1700` · `{{H2_COUNT}}` = `6`
- `{{LB_PRODUCT_URL}}` = `https://leafandbird.com/products/peptide-eye-gel-cream`

Meta JSON values:
```json
{
  "title_tag": "Caffeine-Free Eye Cream: Why I Switched (2026)",
  "meta_desc": "I used to think caffeine eye cream was the only option for tired-mom eyes. Here's what changed my mind — and what I use now.",
  "image_alt": "Caffeine-free eye cream jar beside an empty espresso cup — caffeine free eye cream"
}
```

- [ ] **Step A: Generate featured image** (per Pattern Step A)
- [ ] **Step B: Write `drafts/03-caffeine-free-eye-cream-why.html`** (per Pattern Step B; word target 1,700; H2 sequence above; include 1 citation on topical caffeine research)
- [ ] **Step C: Write `meta/03-caffeine-free-eye-cream-why.json`** (per Pattern Step C; with values above)
- [ ] **Step D: Publish + verify** (per Pattern Step D)

---

## Task 5: Article #4 — `acetyl-tetrapeptide-5-explained`

**Files:**
- Create: drafts/04, meta/04, images/04

**Article spec:**
- Slug: `acetyl-tetrapeptide-5-explained`
- Working title: "Acetyl Tetrapeptide-5: What This Eye Cream Ingredient Actually Does"
- Primary keyword: `acetyl tetrapeptide-5`
- Word target: 1,800 (±10%)
- L&B link: peptide eye gel-cream
- Required H2 sequence:
  1. What Is Acetyl Tetrapeptide-5?
  2. How It Compares to Other Peptides You'll See on Labels
  3. What the Research Actually Shows
  4. Is It Pregnancy-Safe?
  5. Where I Find It in My Routine
  6. Frequently Asked Questions
- Internal HF links: article #1, article #2, article #3, Health & Wellness category
- Citation required: 1 PubMed/research source on acetyl tetrapeptide-5 efficacy

**Image prompt:**
> "Macro of a clear glass dropper releasing a single drop of clear serum onto a green leaf, soft cyan-teal lighting, scientific clean editorial styling. 16:9. No text."

**Parameter substitution:**
- `{{NN}}` = `04` · `{{SLUG}}` = `acetyl-tetrapeptide-5-explained` · `{{TITLE}}` = `Acetyl Tetrapeptide-5: What This Eye Cream Ingredient Actually Does`
- `{{FOCUS_KW}}` = `acetyl tetrapeptide-5` · `{{WORD_TARGET}}` = `1800` · `{{H2_COUNT}}` = `6`
- `{{LB_PRODUCT_URL}}` = `https://leafandbird.com/products/peptide-eye-gel-cream`

Meta JSON values:
```json
{
  "title_tag": "Acetyl Tetrapeptide-5: What It Actually Does for Eyes",
  "meta_desc": "Acetyl Tetrapeptide-5 keeps showing up on eye cream labels. Here's what it actually does, the research behind it, and whether it's pregnancy-safe.",
  "image_alt": "Glass dropper releasing serum onto a green leaf — acetyl tetrapeptide-5 explained"
}
```

- [ ] **Step A: Generate featured image** (per Pattern Step A)
- [ ] **Step B: Write `drafts/04-acetyl-tetrapeptide-5-explained.html`** (per Pattern Step B; word target 1,800; H2 sequence above; include 1 PubMed citation on acetyl tetrapeptide-5 efficacy)
- [ ] **Step C: Write `meta/04-acetyl-tetrapeptide-5-explained.json`** (per Pattern Step C)
- [ ] **Step D: Publish + verify** (per Pattern Step D)

---

## Task 6: Article #5 — `whipped-tallow-cream-review`

**Files:**
- Create: drafts/05, meta/05, images/05

**Article spec:**
- Slug: `whipped-tallow-cream-review`
- Working title: "I Tested Whipped Tallow Cream for 60 Days — Here's My Honest Take"
- Primary keyword: `whipped tallow cream review`
- Word target: 2,200 (±10%)
- L&B link: link to all 3 tallow variants (`tallow-cream-lemongrass-lavender`, `tallow-cream-orange-bergamot`, `tallow-cream-peaceful-night`) plus the collection `https://leafandbird.com/collections/tallow-cream`
- Required H2 sequence:
  1. What Tallow Is and Why I Started Using It
  2. The First Week: What to Expect
  3. Day 30: My Skin's Honest Reaction
  4. Day 60: What Stuck and What Surprised Me
  5. The 3 Scents I've Tried (and Which One I Reach For Most)
  6. What I'd Tell Someone Buying Their First Tallow Cream
  7. Frequently Asked Questions
- Internal HF links: article #6 (tallow vs drugstore), article #7 (pregnancy-safe tallow), Health & Wellness category
- No citation required (review piece)

**Image prompt:**
> "Three small skincare jars in a row on raw beechwood, beeswax candle and dried herbs nearby, golden hour warm light, ancestral homestead aesthetic. 16:9. No text."

**Voice note for this article and Tasks 7 & 8:** warm/ancestral tone (grass-fed, "what our grandmothers used"). Frame tallow as ancestral, not as vegan — these are animal-derived products.

**Parameter substitution:**
- `{{NN}}` = `05` · `{{SLUG}}` = `whipped-tallow-cream-review` · `{{TITLE}}` = `I Tested Whipped Tallow Cream for 60 Days — Here's My Honest Take`
- `{{FOCUS_KW}}` = `whipped tallow cream review` · `{{WORD_TARGET}}` = `2200` · `{{H2_COUNT}}` = `7`
- `{{LB_PRODUCT_URL}}` = `https://leafandbird.com/collections/tallow-cream` *(plus 3 individual variant links in body)*

Meta JSON values:
```json
{
  "title_tag": "Whipped Tallow Cream Review: 60 Days of Honest Notes (2026)",
  "meta_desc": "I switched to whipped tallow cream and tracked what actually happened over 60 days. Here's the day-1, day-30, and day-60 honest take.",
  "image_alt": "Three whipped tallow cream jars on raw beechwood — whipped tallow cream review"
}
```

- [ ] **Step A: Generate featured image** (per Pattern Step A)
- [ ] **Step B: Write `drafts/05-whipped-tallow-cream-review.html`** (per Pattern Step B; word target 2,200; warm/ancestral voice; reference all 3 variants by name; verify check needs `'{{LB_PRODUCT_URL}}' in body` plus all 3 variant URLs)
- [ ] **Step C: Write `meta/05-whipped-tallow-cream-review.json`** (per Pattern Step C)
- [ ] **Step D: Publish + verify** (per Pattern Step D)

---

## Task 7: Article #6 — `beef-tallow-vs-drugstore-moisturizer`

**Files:**
- Create: drafts/06, meta/06, images/06

**Article spec:**
- Slug: `beef-tallow-vs-drugstore-moisturizer`
- Working title: "Beef Tallow vs. Drugstore Moisturizer: A Homesteader's Comparison"
- Primary keyword: `tallow vs drugstore moisturizer`
- Word target: 1,900 (±10%)
- L&B link: tallow collection + 1 specific tallow variant
- Required H2 sequence:
  1. Quick Comparison at a Glance (use a comparison table)
  2. Ingredient Lists Side by Side
  3. Cost Per Use Over a Year
  4. Skin Feel: A Real Test
  5. When Drugstore Still Makes Sense
  6. When Tallow Is the Right Move
  7. Frequently Asked Questions
- Internal HF links: article #5, article #7, Health & Wellness category
- Citation: 1 source on common drugstore moisturizer ingredient (e.g., mineral oil, dimethicone) skin penetration / safety profile

**Image prompt:**
> "Side-by-side flat lay of a clay-toned skincare jar (artisan) and a generic plastic drugstore moisturizer pump bottle on a warm linen surface. Editorial honest comparison vibe. 16:9. No text."

**Parameter substitution:**
- `{{NN}}` = `06` · `{{SLUG}}` = `beef-tallow-vs-drugstore-moisturizer` · `{{TITLE}}` = `Beef Tallow vs. Drugstore Moisturizer: A Homesteader's Comparison`
- `{{FOCUS_KW}}` = `tallow vs drugstore moisturizer` · `{{WORD_TARGET}}` = `1900` · `{{H2_COUNT}}` = `7`
- `{{LB_PRODUCT_URL}}` = `https://leafandbird.com/collections/tallow-cream` *(plus 1 specific variant)*

Meta JSON values:
```json
{
  "title_tag": "Tallow vs. Drugstore Moisturizer: A Homesteader's Compare (2026)",
  "meta_desc": "Tallow cream or drugstore moisturizer? I compared ingredient lists, skin feel, cost-per-use, and when each one actually makes sense.",
  "image_alt": "Tallow jar beside a drugstore moisturizer bottle on linen — tallow vs drugstore moisturizer"
}
```

- [ ] **Step A: Generate featured image** (per Pattern Step A)
- [ ] **Step B: Write `drafts/06-beef-tallow-vs-drugstore-moisturizer.html`** (per Pattern Step B; warm/ancestral voice; word target 1,900; H2 #1 must include an HTML comparison table; include 1 citation on common drugstore ingredient skin penetration / safety)
- [ ] **Step C: Write `meta/06-beef-tallow-vs-drugstore-moisturizer.json`** (per Pattern Step C)
- [ ] **Step D: Publish + verify** (per Pattern Step D)

---

## Task 8: Article #7 — `pregnancy-safe-tallow-skincare`

**Files:**
- Create: drafts/07, meta/07, images/07

**Article spec:**
- Slug: `pregnancy-safe-tallow-skincare`
- Working title: "Pregnancy-Safe Tallow Skincare: What's in It and What to Watch For"
- Primary keyword: `pregnancy safe tallow`
- Word target: 1,800 (±10%)
- L&B link: tallow collection + `tallow-cream-lemongrass-lavender` (the all-rounder, gentlest)
- Required H2 sequence:
  1. Why I Looked at Tallow During Pregnancy
  2. What's Actually in Whipped Tallow Cream (and Why It's Pregnancy-Friendly)
  3. The Ingredients to Watch in Some Tallow Brands
  4. The Tallow I Used (Postpartum Especially)
  5. Quick Reference: What's Safe, What to Skip
  6. Frequently Asked Questions
- Internal HF links: article #5, article #6, article #2 (eye cream pregnancy)
- Citation required (pregnancy): 1 ACOG / Mayo / NIH source on essential oils or topical safety in pregnancy

**Image prompt:**
> "Macro of a soft cream-toned skincare jar on a hand-knit baby blanket in cream/oat color, gentle window light, no baby visible, postpartum-cozy aesthetic. 16:9. No text."

**Parameter substitution:**
- `{{NN}}` = `07` · `{{SLUG}}` = `pregnancy-safe-tallow-skincare` · `{{TITLE}}` = `Pregnancy-Safe Tallow Skincare: What's in It and What to Watch For`
- `{{FOCUS_KW}}` = `pregnancy safe tallow` · `{{WORD_TARGET}}` = `1800` · `{{H2_COUNT}}` = `6`
- `{{LB_PRODUCT_URL}}` = `https://leafandbird.com/products/tallow-cream-lemongrass-lavender` *(also link the tallow collection)*

Meta JSON values:
```json
{
  "title_tag": "Pregnancy-Safe Tallow Skincare: What's Actually OK (2026)",
  "meta_desc": "Whipped tallow cream during pregnancy: which formulas are safe, which to skip, and the one I reached for postpartum. Honest, ingredient-by-ingredient.",
  "image_alt": "Tallow cream jar on a knit baby blanket — pregnancy safe tallow skincare"
}
```

- [ ] **Step A: Generate featured image** (per Pattern Step A)
- [ ] **Step B: Write `drafts/07-pregnancy-safe-tallow-skincare.html`** (per Pattern Step B; warm/ancestral voice; word target 1,800; include 1 ACOG/Mayo/NIH citation on essential oils or topical safety in pregnancy)
- [ ] **Step C: Write `meta/07-pregnancy-safe-tallow-skincare.json`** (per Pattern Step C)
- [ ] **Step D: Publish + verify** (per Pattern Step D)

---

## Task 9: Article #8 — `what-is-pdrn-homesteader-take`

**Files:**
- Create: drafts/08, meta/08, images/08

**Article spec:**
- Slug: `what-is-pdrn-homesteader-take`
- Working title: "What Is PDRN? A Homesteader's Honest Take on K-Beauty's Hottest Ingredient"
- Primary keyword: `what is pdrn`
- Word target: 2,000 (±10%)
- L&B link: `https://leafandbird.com/products/pdrn-brightening-serum`
- Required H2 sequence:
  1. The First Time I Heard "PDRN"
  2. What PDRN Actually Is (in Plain English)
  3. Why It Blew Up in K-Beauty
  4. The One Thing Most PDRN Products Have That I Won't Use
  5. The Vegan PDRN I Found (and What I Think About It)
  6. Should You Try PDRN? My Honest Take
  7. Frequently Asked Questions
- Internal HF links: article #9, article #10, Health & Wellness category, GLP-3 pillar (cross-cluster bridge — both are "natural-health peptides" angle)
- Citation: 1 PubMed source on PDRN clinical research

**Image prompt:**
> "Macro of a clear glass serum bottle with white label on white marble background, single droplet falling from the dropper, clean clinical editorial. 16:9. No text."

**Voice note for this article and Tasks 10 & 11:** clinical/scientific tone — K-beauty roots, clean-active framing. PDRN content sounds different from tallow content (which is ancestral).

**Parameter substitution:**
- `{{NN}}` = `08` · `{{SLUG}}` = `what-is-pdrn-homesteader-take` · `{{TITLE}}` = `What Is PDRN? A Homesteader's Honest Take on K-Beauty's Hottest Ingredient`
- `{{FOCUS_KW}}` = `what is pdrn` · `{{WORD_TARGET}}` = `2000` · `{{H2_COUNT}}` = `7`
- `{{LB_PRODUCT_URL}}` = `https://leafandbird.com/products/pdrn-brightening-serum`

Meta JSON values:
```json
{
  "title_tag": "What Is PDRN? A Homesteader's Honest Take on K-Beauty (2026)",
  "meta_desc": "PDRN is everywhere in Korean skincare — but what is it actually? Here's a homesteader's plain-English explainer and the one thing I won't use it without.",
  "image_alt": "Clear glass PDRN serum bottle on white marble — what is PDRN"
}
```

- [ ] **Step A: Generate featured image** (per Pattern Step A)
- [ ] **Step B: Write `drafts/08-what-is-pdrn-homesteader-take.html`** (per Pattern Step B; clinical voice; word target 2,000; include 1 PubMed citation on PDRN clinical research; include link to GLP-3 pillar as cross-cluster bridge)
- [ ] **Step C: Write `meta/08-what-is-pdrn-homesteader-take.json`** (per Pattern Step C)
- [ ] **Step D: Publish + verify** (per Pattern Step D)

---

## Task 10: Article #9 — `vegan-pdrn-why-it-matters`

**Files:**
- Create: drafts/09, meta/09, images/09

**Article spec:**
- Slug: `vegan-pdrn-why-it-matters`
- Working title: "Vegan PDRN Serum: Why It's Hard to Find (and Why That Matters)"
- Primary keyword: `vegan pdrn serum`
- Word target: 1,800 (±10%)
- L&B link: `https://leafandbird.com/products/pdrn-brightening-serum` (the moat product)
- Required H2 sequence:
  1. Where Most PDRN Comes From
  2. Why That's a Problem for a Lot of Us
  3. Is Vegan PDRN Even Possible?
  4. The One Brand I Found Doing It Right
  5. What to Look For on the Label
  6. Frequently Asked Questions
- Internal HF links: article #8, article #10, Health & Wellness category
- Citation: 1 source on PDRN sourcing methods (typically salmon-derived) and one on alternative bioregenerative compounds

**Image prompt:**
> "Macro flat-lay of a serum bottle on a bed of green leaves and white petals, soft clinical lighting with green accents, plant-derived editorial. 16:9. No text."

**Parameter substitution:**
- `{{NN}}` = `09` · `{{SLUG}}` = `vegan-pdrn-why-it-matters` · `{{TITLE}}` = `Vegan PDRN Serum: Why It's Hard to Find (and Why That Matters)`
- `{{FOCUS_KW}}` = `vegan pdrn serum` · `{{WORD_TARGET}}` = `1800` · `{{H2_COUNT}}` = `6`
- `{{LB_PRODUCT_URL}}` = `https://leafandbird.com/products/pdrn-brightening-serum`

Meta JSON values:
```json
{
  "title_tag": "Vegan PDRN Serum: Why It's So Rare (and What to Buy)",
  "meta_desc": "Most PDRN comes from salmon. Here's why that matters, whether vegan PDRN is even possible, and the one brand I found doing it right.",
  "image_alt": "Vegan PDRN serum bottle on green leaves and petals — vegan pdrn serum"
}
```

- [ ] **Step A: Generate featured image** (per Pattern Step A)
- [ ] **Step B: Write `drafts/09-vegan-pdrn-why-it-matters.html`** (per Pattern Step B; clinical voice; word target 1,800; include 1 citation on PDRN sourcing — typically salmon-derived — and 1 on alternative bioregenerative compounds)
- [ ] **Step C: Write `meta/09-vegan-pdrn-why-it-matters.json`** (per Pattern Step C)
- [ ] **Step D: Publish + verify** (per Pattern Step D)

---

## Task 11: Article #10 — `pdrn-vs-retinol-pregnancy`

**Files:**
- Create: drafts/10, meta/10, images/10

**Article spec:**
- Slug: `pdrn-vs-retinol-pregnancy`
- Working title: "PDRN vs. Retinol During Pregnancy: Why I Made the Switch"
- Primary keyword: `pdrn vs retinol pregnancy`
- Word target: 1,900 (±10%)
- L&B link: PDRN serum + eye gel-cream (both pregnancy-safe options)
- Required H2 sequence:
  1. Why Retinol Is Off the Table in Pregnancy
  2. What I Used to Reach For (and Why I Couldn't Anymore)
  3. Where PDRN Comes In
  4. PDRN vs. Retinol: A Side-by-Side
  5. The Vegan PDRN Serum I Switched To
  6. What I'd Tell My Pregnant Friend Asking This Question
  7. Frequently Asked Questions
- Internal HF links: article #2, article #7, article #8, article #9
- Citations required: 1 ACOG/Mayo source on retinol contraindication in pregnancy; 1 PMID/PubMed on PDRN safety profile

**Image prompt:**
> "Side-by-side macro of two small dropper bottles on a white linen surface — one labeled with botanical green tones, one with neutral cream tones — soft daylight. 16:9. No text."

**Parameter substitution:**
- `{{NN}}` = `10` · `{{SLUG}}` = `pdrn-vs-retinol-pregnancy` · `{{TITLE}}` = `PDRN vs. Retinol During Pregnancy: Why I Made the Switch`
- `{{FOCUS_KW}}` = `pdrn vs retinol pregnancy` · `{{WORD_TARGET}}` = `1900` · `{{H2_COUNT}}` = `7`
- `{{LB_PRODUCT_URL}}` = `https://leafandbird.com/products/pdrn-brightening-serum` *(also link the eye gel-cream as a complementary pregnancy-safe option)*

Meta JSON values:
```json
{
  "title_tag": "PDRN vs. Retinol in Pregnancy: Why I Switched (2026)",
  "meta_desc": "Retinol is off the table in pregnancy. Here's where PDRN fits, how it compares, and the vegan PDRN serum I actually switched to.",
  "image_alt": "Two dropper bottles side by side — pdrn vs retinol pregnancy"
}
```

- [ ] **Step A: Generate featured image** (per Pattern Step A)
- [ ] **Step B: Write `drafts/10-pdrn-vs-retinol-pregnancy.html`** (per Pattern Step B; clinical voice; word target 1,900; include 1 ACOG/Mayo citation on retinol contraindication in pregnancy AND 1 PMID/PubMed citation on PDRN safety profile; H2 #4 must include a side-by-side comparison)
- [ ] **Step C: Write `meta/10-pdrn-vs-retinol-pregnancy.json`** (per Pattern Step C)
- [ ] **Step D: Publish + verify** (per Pattern Step D)

---

## Task 12: Final batch verification

**Files:**
- Update: `/Users/skitch/hf-leafbird-articles/manifest.json` (verified state)
- Create: `/Users/skitch/hf-leafbird-articles/REVERT.sh`

- [ ] **Step 1: Confirm all 10 manifest entries**

```bash
python3 -c "
import json
m = json.load(open('/Users/skitch/hf-leafbird-articles/manifest.json'))
assert len(m['articles']) == 10, f'expected 10, got {len(m[\"articles\"])}'
for a in m['articles']:
    assert a['id'] and a['link'], a
print('manifest has 10 articles, all with id+link')
"
```

- [ ] **Step 2: Sanity-check all 10 URLs return 200 + contain disclosure + L&B link**

```bash
python3 - <<'PY'
import urllib.request, json, time
m = json.load(open('/Users/skitch/hf-leafbird-articles/manifest.json'))
ts = int(time.time())
fails = []
for a in m['articles']:
    try:
        req = urllib.request.Request(f"{a['link']}?cb={ts}", headers={"User-Agent":"Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8','ignore')
        ok = ("I co-own Leaf" in html) and ("leafandbird.com/products/" in html)
        if not ok: fails.append((a['slug'], "missing disclosure or product link"))
    except Exception as e:
        fails.append((a['slug'], str(e)))
print('FAILS:', fails or "none")
PY
```

Expected: `FAILS: none`.

- [ ] **Step 3: Diversity check — no two articles have identical H2 sequences**

```bash
python3 - <<'PY'
import re, pathlib, hashlib
drafts = sorted(pathlib.Path('/Users/skitch/hf-leafbird-articles/drafts').glob('*.html'))
seen = {}
for d in drafts:
    body = d.read_text()
    h2s = [re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',h)).strip().lower()
           for h in re.findall(r'<h2[^>]*>(.*?)</h2>', body, re.DOTALL|re.IGNORECASE)]
    sig = "|".join(h2s)
    if sig in seen:
        print(f"DUPLICATE H2 SEQUENCE: {d.name} matches {seen[sig]}")
        raise SystemExit(1)
    seen[sig] = d.name
print(f"all {len(drafts)} articles have distinct H2 sequences")
PY
```

Expected: `all 10 articles have distinct H2 sequences`.

- [ ] **Step 4: Write `REVERT.sh`**

```bash
cat > /Users/skitch/hf-leafbird-articles/REVERT.sh <<'BASH'
#!/usr/bin/env bash
# Unpublish (set draft) all 10 HF×LB articles. Idempotent. Does NOT delete media.
python3 - <<'PY'
import urllib.request, base64, json
auth = base64.b64encode(b"fred:Md7C 1cWk yhcX jmfs ffin lrZ6").decode()
m = json.load(open('/Users/skitch/hf-leafbird-articles/manifest.json'))
for a in m['articles']:
    req = urllib.request.Request(
        f"https://homesteadfanatic.com/wp-json/wp/v2/posts/{a['id']}",
        data=json.dumps({"status":"draft"}).encode(), method="POST",
    )
    req.add_header("Authorization", f"Basic {auth}")
    req.add_header("User-Agent", "Mozilla/5.0 (Macintosh)")
    req.add_header("Content-Type", "application/json")
    print(urllib.request.urlopen(req).status, a['slug'])
PY
BASH
chmod +x /Users/skitch/hf-leafbird-articles/REVERT.sh
```

---

## Task 13: Commit + memory update

**Files:**
- Modify: home directory git index
- Modify: `~/.claude/projects/-Users-skitch/memory/project_homestead_fanatic.md` (or wherever the HF project memory lives)

- [ ] **Step 1: Stage artifacts**

```bash
cd /Users/skitch
git add homesteadfanatic-leafbird-articles-spec.md homesteadfanatic-leafbird-articles-plan.md hf-leafbird-articles/
git status --short | grep -E 'homesteadfanatic-leafbird|hf-leafbird' | head -30
```

- [ ] **Step 2: Commit**

```bash
git commit -m "$(cat <<'EOF'
Ship 10 HF × Leaf & Bird articles (eye cream / tallow / vegan PDRN)

Cornerstone natural-skincare batch on homesteadfanatic.com featuring
leafandbird.com products. Sarah Kate Wilder voice, FTC ownership disclosure
on every article, all live and cross-linked. Manifest tracks 10 post IDs;
REVERT.sh unpublishes the entire batch in one command.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 3: Update HF project memory** to reference the new cluster (article slugs + IDs from manifest), the new "Natural Skincare on the Homestead" cluster pillar (cross-bridge to GLP-3), and the FTC disclosure pattern for owned-brand recommendations.

---

## Acceptance Criteria (final batch)

- [ ] All 10 articles published with status `publish`
- [ ] Each article has FTC disclosure block visible above the first H2
- [ ] Each article links to at least one leafandbird.com product
- [ ] Each article meets ±10% word target
- [ ] Each article passes the diversity check (no two articles share identical H2 sequences)
- [ ] `manifest.json` has 10 entries each with `id` + `link`
- [ ] All 10 URLs return HTTP 200
- [ ] `REVERT.sh` exists and is executable
- [ ] Git commit recorded

---

## Reversibility

```bash
bash /Users/skitch/hf-leafbird-articles/REVERT.sh
```

This sets `status: draft` on all 10 articles. URLs will 404 publicly but data and media are preserved. Re-publishing requires re-running step 5 of each article task, OR a `status: publish` PATCH against each id.

To delete entirely (irreversible):
```bash
python3 -c "
import urllib.request, base64, json
auth = base64.b64encode(b'fred:Md7C 1cWk yhcX jmfs ffin lrZ6').decode()
m = json.load(open('/Users/skitch/hf-leafbird-articles/manifest.json'))
for a in m['articles']:
    req = urllib.request.Request(
        f\"https://homesteadfanatic.com/wp-json/wp/v2/posts/{a['id']}?force=true\",
        method='DELETE',
    )
    req.add_header('Authorization', f'Basic {auth}')
    req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh)')
    print(urllib.request.urlopen(req).status, a['slug'])
"
```
