# Homestead Fanatic Homepage Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the homesteadfanatic.com homepage (WP page ID 8) with a hybrid editorial+warmth design covering 8 purpose-built sections, deployed via WP REST API with a one-command revert path.

**Architecture:** All HTML for the new homepage is assembled locally as a single `<div class="hf-home">` block with an inline `<style>` element at the top (scoped under `.hf-home-*`), then pushed to page 8 via `POST /wp/v2/pages/8`. Sections 6 and 7 (latest gear + latest posts) are rendered statically — data is pulled once at deploy time from the WP REST API and baked into the HTML. No runtime JS, no carousels, no popups. The newsletter form posts to LeadConnector.

**Tech Stack:** WordPress REST API (`wp/v2`), GeneratePress theme (unchanged), Google Fonts (Lora + Inter), HTML/CSS only — no JS framework, no PHP edits.

**Spec reference:** `/Users/skitch/homesteadfanatic-homepage-redesign-spec.md`

**Working directory for local artifacts:** `/Users/skitch/hf-homepage/` (create at task 1)

**API credentials (in env-style for tasks):**
- `WP_USER=fred`
- `WP_PASS="Md7C 1cWk yhcX jmfs ffin lrZ6"`
- `WP_BASE=https://homesteadfanatic.com/wp-json/wp/v2`
- `UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"`

---

## File Structure

All task output is created under `/Users/skitch/hf-homepage/` to keep the local repo (home directory) tidy:

```
hf-homepage/
  backup-page-8-2026-04-25.json     # full GET response for original page (Task 1)
  backup-page-8-2026-04-25.html     # original content.rendered (Task 1)
  asset-manifest.json               # hero photo, 6 topic tiles, pillar image URLs (Task 4)
  dynamic-posts.json                # 3 gear + 3 latest posts payload (Task 3)
  lc-form.json                      # discovered LeadConnector endpoint + field names (Task 2)
  homepage.css                      # all .hf-home-* styles, single block (Task 5)
  sections/
    01-hero.html                    # Task 6
    02-pillar.html                  # Task 7
    03-topics.html                  # Task 8
    04-author.html                  # Task 9
    05-health.html                  # Task 10
    06-gear.html                    # Task 11
    07-latest.html                  # Task 12
    08-newsletter.html              # Task 13
  homepage.html                     # full assembled page content (Task 14)
  deploy-result.json                # WP API response after push (Task 14)
```

---

## Task 1: Backup current homepage

**Why:** Reversibility. Every later task assumes we can restore the original homepage with a single REST call.

**Files:**
- Create: `/Users/skitch/hf-homepage/backup-page-8-2026-04-25.json`
- Create: `/Users/skitch/hf-homepage/backup-page-8-2026-04-25.html`

- [ ] **Step 1: Create working directory**

```bash
mkdir -p /Users/skitch/hf-homepage/sections
```

- [ ] **Step 2: Pull current page 8 and save the full JSON**

```bash
curl -s -u "$WP_USER:$WP_PASS" -H "User-Agent: $UA" \
  "$WP_BASE/pages/8?context=edit" \
  > /Users/skitch/hf-homepage/backup-page-8-2026-04-25.json
```

Verify: `ls -lh /Users/skitch/hf-homepage/backup-page-8-2026-04-25.json` shows non-zero size; `python3 -c "import json; d=json.load(open('/Users/skitch/hf-homepage/backup-page-8-2026-04-25.json')); print(d['id'], d['slug'])"` prints `8 home`.

- [ ] **Step 3: Extract `content.raw` to a clean HTML file**

```bash
python3 - <<'PY'
import json
d = json.load(open('/Users/skitch/hf-homepage/backup-page-8-2026-04-25.json'))
open('/Users/skitch/hf-homepage/backup-page-8-2026-04-25.html','w').write(d['content']['raw'])
print('bytes:', len(d['content']['raw']))
PY
```

Expected: prints a non-zero byte count.

- [ ] **Step 4: Document the revert command in the backup file's first line**

The revert command is:

```bash
python3 - <<'PY'
import json, urllib.request, base64
auth = base64.b64encode(b"fred:Md7C 1cWk yhcX jmfs ffin lrZ6").decode()
content = open('/Users/skitch/hf-homepage/backup-page-8-2026-04-25.html').read()
req = urllib.request.Request(
    "https://homesteadfanatic.com/wp-json/wp/v2/pages/8",
    data=json.dumps({"content": content}).encode(),
    method="POST",
)
req.add_header("Authorization", f"Basic {auth}")
req.add_header("User-Agent", "Mozilla/5.0 (Macintosh)")
req.add_header("Content-Type", "application/json")
print(urllib.request.urlopen(req).status)
PY
```

Save this as `/Users/skitch/hf-homepage/REVERT.sh` for emergency use.

---

## Task 2: Discover LeadConnector form endpoint

**Why:** Section 8 needs to post to LeadConnector. We need to know the actual POST URL and field names before writing the form.

**Files:**
- Create: `/Users/skitch/hf-homepage/lc-form.json`

- [ ] **Step 1: Pull current homepage HTML and any other LC-using pages and grep for LC form embed signatures**

```bash
curl -s -H "User-Agent: $UA" "https://homesteadfanatic.com/" > /tmp/hf_home.html
grep -oE 'https://[^"]*leadconnectorhq[^"]*' /tmp/hf_home.html | sort -u
grep -oE 'data-form-id="[^"]*"' /tmp/hf_home.html | sort -u
grep -oE 'src="[^"]*api/v[0-9]+/forms[^"]*"' /tmp/hf_home.html | sort -u
```

If results are empty, also fetch the `/contact-us/` or `/about-2/` pages and repeat. If still empty, fall through to step 2.

- [ ] **Step 2: Look for LeadConnector plugin REST routes**

```bash
curl -s "https://homesteadfanatic.com/wp-json/" | python3 -c "import json,sys; d=json.load(sys.stdin); print('\n'.join(n for n in d.get('namespaces',[]) if 'lc' in n.lower() or 'lead' in n.lower()))"
```

Then introspect each LC namespace:

```bash
curl -s -u "$WP_USER:$WP_PASS" -H "User-Agent: $UA" \
  "https://homesteadfanatic.com/wp-json/lc_public_api/v1" | python3 -m json.tool | head -80
```

- [ ] **Step 3: Save discovered endpoint + field names to `lc-form.json`**

If a form embed URL is found, structure looks like:

```json
{
  "action_url": "https://api.leadconnectorhq.com/widget/form/<formId>",
  "form_id": "<formId>",
  "method": "POST",
  "fields": {
    "email": "email"
  },
  "discovered_via": "homepage embed"
}
```

If nothing is found, set:

```json
{
  "action_url": null,
  "fallback": "Use mailto:fred@konversly.com on the form, or insert plain HTML form that posts to a placeholder action and document this gap in the deploy-result.json. Do NOT block the deploy."
}
```

- [ ] **Step 4: Verify the file is parseable**

```bash
python3 -c "import json; print(json.load(open('/Users/skitch/hf-homepage/lc-form.json')))"
```

---

## Task 3: Pull dynamic post data for sections 6 + 7

**Why:** Sections 6 (Latest Gear) and 7 (Latest Posts) need 3 cards each, baked statically at deploy time.

**Files:**
- Create: `/Users/skitch/hf-homepage/dynamic-posts.json`

- [ ] **Step 1: Pull 3 most recent posts in Homesteading Tools (17) or Survival & Prepping (9)**

```bash
curl -s -u "$WP_USER:$WP_PASS" -H "User-Agent: $UA" \
  "$WP_BASE/posts?categories=17,9&per_page=3&orderby=date&_embed=wp:featuredmedia&_fields=id,slug,title,link,excerpt,categories,_links,_embedded" \
  > /tmp/hf_gear.json
python3 -c "import json; d=json.load(open('/tmp/hf_gear.json')); print(len(d), 'gear posts')"
```

Expected: `3 gear posts`.

- [ ] **Step 2: Pull the 6 most recent posts overall, then filter out any IDs already in the gear set**

```bash
curl -s -u "$WP_USER:$WP_PASS" -H "User-Agent: $UA" \
  "$WP_BASE/posts?per_page=6&orderby=date&_embed=wp:featuredmedia&_embed=wp:term&_fields=id,slug,title,link,excerpt,categories,_links,_embedded" \
  > /tmp/hf_latest.json
```

- [ ] **Step 3: Build `dynamic-posts.json` with normalized card payloads**

```bash
python3 - <<'PY'
import json
gear = json.load(open('/tmp/hf_gear.json'))
latest = json.load(open('/tmp/hf_latest.json'))
gear_ids = {p['id'] for p in gear}
latest_filtered = [p for p in latest if p['id'] not in gear_ids][:3]

def to_card(p, eyebrow):
    media = p.get('_embedded',{}).get('wp:featuredmedia',[{}])[0]
    img = media.get('source_url','')
    img_alt = media.get('alt_text','') or p['title']['rendered']
    excerpt = p['excerpt']['rendered']
    # strip tags from excerpt
    import re
    excerpt = re.sub(r'<[^>]+>','',excerpt).strip()
    if len(excerpt) > 140: excerpt = excerpt[:137].rsplit(' ',1)[0] + '…'
    return {
        "title": p['title']['rendered'],
        "url": p['link'],
        "image": img,
        "image_alt": img_alt,
        "excerpt": excerpt,
        "eyebrow": eyebrow,
    }

out = {
    "gear": [to_card(p, "Gear Review") for p in gear],
    "latest": [to_card(p, "Latest") for p in latest_filtered],
}
json.dump(out, open('/Users/skitch/hf-homepage/dynamic-posts.json','w'), indent=2)
print('gear cards:', len(out['gear']))
print('latest cards:', len(out['latest']))
PY
```

Expected: `gear cards: 3` and `latest cards: 3`.

- [ ] **Step 4: Verify each card has a non-empty image URL**

```bash
python3 -c "
import json
d = json.load(open('/Users/skitch/hf-homepage/dynamic-posts.json'))
for k,v in d.items():
    for c in v:
        assert c['image'], f'missing image: {c[\"title\"]}'
        assert c['url'].startswith('https://'), f'bad url: {c[\"url\"]}'
print('all cards valid')
"
```

Expected: `all cards valid`.

---

## Task 4: Resolve visual assets (hero photo + 6 topic tiles + pillar image)

**Why:** Hardcoded image URLs for sections 1, 2, 3.

**Files:**
- Create: `/Users/skitch/hf-homepage/asset-manifest.json`

- [ ] **Step 1: Find Sarah Kate's portrait in media library**

```bash
curl -s -u "$WP_USER:$WP_PASS" -H "User-Agent: $UA" \
  "$WP_BASE/media?search=sarah-kate&per_page=10&_fields=id,source_url,alt_text,title" \
  | python3 -m json.tool
```

Save the `source_url` for the portrait file (`sarah-kate-wilder.jpg`).

- [ ] **Step 2: Find featured image for the pillar story (`/homesteading-skills-beginners/`, post slug)**

```bash
curl -s -u "$WP_USER:$WP_PASS" -H "User-Agent: $UA" \
  "$WP_BASE/posts?slug=homesteading-skills-beginners&_embed=wp:featuredmedia&_fields=id,title,link,_embedded" \
  | python3 -c "
import json,sys
p = json.load(sys.stdin)[0]
m = p['_embedded']['wp:featuredmedia'][0]
print(p['link'])
print(m['source_url'])
print(p['title']['rendered'])
"
```

Capture: pillar image URL, pillar URL, pillar title.

- [ ] **Step 3: Pick one representative featured image per topic category**

For each of the 6 categories below, pull 1 representative post (most recent post with a featured image) and grab its featured image URL:

```bash
python3 - <<'PY'
import json, urllib.request, base64
auth = base64.b64encode(b"fred:Md7C 1cWk yhcX jmfs ffin lrZ6").decode()
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

CATS = [
  (9,  "Survival & Prepping",  "https://homesteadfanatic.com/category/survival-prepping/", 21),
  (13, "Off-Grid Living",      "https://homesteadfanatic.com/category/off-grid-living/",   17),
  (18, "Health & Wellness",    "https://homesteadfanatic.com/category/health-wellness/",   16),
  (17, "Homesteading Tools",   "https://homesteadfanatic.com/category/homesteading-tools/",12),
  (15, "Emergency Food",       "https://homesteadfanatic.com/category/emergency-food/",    10),
  (12, "Food Preservation",    "https://homesteadfanatic.com/category/food-preservation/",  8),
]

tiles = []
for cat_id, name, url, count in CATS:
    api = f"https://homesteadfanatic.com/wp-json/wp/v2/posts?categories={cat_id}&per_page=1&orderby=date&_embed=wp:featuredmedia&_fields=_embedded"
    req = urllib.request.Request(api, headers={"Authorization":f"Basic {auth}","User-Agent":UA})
    posts = json.loads(urllib.request.urlopen(req).read())
    img = ""
    if posts:
        media = posts[0].get("_embedded",{}).get("wp:featuredmedia",[{}])[0]
        img = media.get("source_url","")
    tiles.append({"name":name,"url":url,"image":img,"count":count})

# Get hero photo
req = urllib.request.Request(
    "https://homesteadfanatic.com/wp-json/wp/v2/media?search=sarah-kate&per_page=5",
    headers={"Authorization":f"Basic {auth}","User-Agent":UA},
)
media = json.loads(urllib.request.urlopen(req).read())
hero = next((m for m in media if "sarah-kate" in m.get("slug","")), media[0] if media else None)
hero_url = hero["source_url"] if hero else ""

# Get pillar image
req = urllib.request.Request(
    "https://homesteadfanatic.com/wp-json/wp/v2/posts?slug=homesteading-skills-beginners&_embed=wp:featuredmedia",
    headers={"Authorization":f"Basic {auth}","User-Agent":UA},
)
pillar_posts = json.loads(urllib.request.urlopen(req).read())
pillar = pillar_posts[0]
pillar_img = pillar["_embedded"]["wp:featuredmedia"][0]["source_url"]

manifest = {
    "hero_photo": hero_url,
    "hero_alt": "Sarah Kate Wilder, founder of Homestead Fanatic",
    "pillar": {
        "url": pillar["link"],
        "title": pillar["title"]["rendered"],
        "image": pillar_img,
    },
    "topic_tiles": tiles,
}
json.dump(manifest, open('/Users/skitch/hf-homepage/asset-manifest.json','w'), indent=2)
print(json.dumps(manifest, indent=2))
PY
```

- [ ] **Step 4: Verify all 6 tiles have an image URL**

```bash
python3 -c "
import json
m = json.load(open('/Users/skitch/hf-homepage/asset-manifest.json'))
assert m['hero_photo'], 'no hero'
assert m['pillar']['image'], 'no pillar image'
for t in m['topic_tiles']:
    assert t['image'], f'no image for {t[\"name\"]}'
print('manifest complete')
"
```

Expected: `manifest complete`.

If any topic tile lacks an image, manually substitute the URL with another suitable image from that category before continuing.

---

## Task 5: Write the homepage CSS

**Why:** All visual styling lives in one inline `<style>` block at the top of the homepage HTML. Single source of truth, easy to revert.

**Files:**
- Create: `/Users/skitch/hf-homepage/homepage.css`

- [ ] **Step 1: Write the full CSS block**

Save this exact content to `/Users/skitch/hf-homepage/homepage.css`:

```css
/* ============ Homestead Fanatic — Homepage ============ */
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@400;500;600;700&display=swap');

.hf-home, .hf-home * { box-sizing: border-box; }
.hf-home {
  --hf-bg: #FAF7F2;
  --hf-text: #1F1F1B;
  --hf-muted: #6B6760;
  --hf-green: #3F5D45;
  --hf-green-dark: #2F4733;
  --hf-tan: #D4A574;
  --hf-tan-soft: #F4E9D7;
  --hf-border: #E8E1D5;
  --hf-card-shadow: 0 2px 8px rgba(31,31,27,0.06);
  --hf-radius: 8px;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  color: var(--hf-text);
  background: var(--hf-bg);
  font-size: 17px;
  line-height: 1.7;
}
.hf-home h1, .hf-home h2, .hf-home h3 { font-family: 'Lora', Georgia, serif; font-weight: 600; line-height: 1.2; margin: 0; color: var(--hf-text); }
.hf-home h1 { font-size: 48px; }
.hf-home h2 { font-size: 32px; }
.hf-home h3 { font-size: 24px; }
.hf-home p  { margin: 0 0 1em 0; }
.hf-home a  { color: var(--hf-green); text-decoration: none; }
.hf-home a:hover { color: var(--hf-green-dark); text-decoration: underline; }
.hf-home img { max-width: 100%; height: auto; display: block; }

.hf-home-section { padding: 80px 0; }
.hf-home-container { max-width: 1200px; margin: 0 auto; padding: 0 32px; }
.hf-home-eyebrow {
  display: inline-block;
  font-family: 'Inter', sans-serif;
  font-size: 12px; font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--hf-green);
  margin-bottom: 12px;
}
.hf-home-btn {
  display: inline-block; padding: 14px 28px;
  font-family: 'Inter', sans-serif; font-weight: 600; font-size: 15px;
  border-radius: var(--hf-radius); border: 2px solid transparent;
  cursor: pointer; transition: all .15s ease;
}
.hf-home-btn-primary { background: var(--hf-green); color: #fff; }
.hf-home-btn-primary:hover { background: var(--hf-green-dark); color: #fff; text-decoration: none; }
.hf-home-btn-outline { background: transparent; color: var(--hf-green); border-color: var(--hf-green); }
.hf-home-btn-outline:hover { background: var(--hf-green); color: #fff; text-decoration: none; }

/* ----- 1. Hero ----- */
.hf-home-hero { padding: 96px 0 80px; }
.hf-home-hero-grid { display: grid; grid-template-columns: 1.4fr 1fr; gap: 64px; align-items: center; }
.hf-home-hero h1 { margin-bottom: 20px; }
.hf-home-hero-sub { font-size: 19px; color: var(--hf-muted); max-width: 520px; margin-bottom: 32px; }
.hf-home-hero-ctas { display: flex; gap: 12px; flex-wrap: wrap; }
.hf-home-hero-photo { width: 100%; max-width: 400px; aspect-ratio: 1; border-radius: 50%; object-fit: cover; margin-left: auto; }

/* ----- 2. Featured Pillar ----- */
.hf-home-pillar { background: #fff; }
.hf-home-pillar-card { display: grid; grid-template-columns: 1fr 1fr; gap: 48px; align-items: center; }
.hf-home-pillar-img { aspect-ratio: 4/3; border-radius: var(--hf-radius); object-fit: cover; }
.hf-home-pillar h2 { margin-bottom: 16px; }
.hf-home-pillar-excerpt { color: var(--hf-muted); font-size: 18px; margin-bottom: 20px; }
.hf-home-pillar a.read-more { font-weight: 600; }

/* ----- 3. Topic Tiles ----- */
.hf-home-topics h2 { text-align: center; margin-bottom: 48px; }
.hf-home-topic-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.hf-home-topic-tile {
  position: relative; aspect-ratio: 4/3; border-radius: var(--hf-radius); overflow: hidden;
  background-size: cover; background-position: center; cursor: pointer;
}
.hf-home-topic-tile a { position: absolute; inset: 0; display: block; }
.hf-home-topic-tile::before {
  content: ''; position: absolute; inset: 0;
  background: linear-gradient(0deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.05) 60%);
  transition: background .3s ease;
}
.hf-home-topic-tile:hover::before { background: linear-gradient(0deg, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.2) 60%); }
.hf-home-topic-tile-title {
  position: absolute; left: 24px; bottom: 20px; right: 24px;
  font-family: 'Lora', serif; font-size: 22px; font-weight: 600; color: #fff;
  z-index: 2;
}
.hf-home-topic-tile-count {
  position: absolute; top: 16px; right: 16px;
  background: rgba(255,255,255,0.95); color: var(--hf-text);
  font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 999px;
  z-index: 2;
}

/* ----- 4. Author Block ----- */
.hf-home-author { background: #fff; }
.hf-home-author-grid { display: grid; grid-template-columns: 280px 1fr; gap: 56px; align-items: center; }
.hf-home-author-photo { width: 280px; aspect-ratio: 1; border-radius: 50%; object-fit: cover; }
.hf-home-author h2 { margin-bottom: 16px; }
.hf-home-author-bio { color: var(--hf-text); font-size: 17px; margin-bottom: 24px; }
.hf-home-author-stats { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 24px; }
.hf-home-author-chip {
  display: inline-block; background: var(--hf-tan-soft); color: var(--hf-text);
  border-radius: 999px; padding: 8px 16px; font-size: 13px; font-weight: 500;
}

/* ----- 5. Health Hub ----- */
.hf-home-health { background: var(--hf-green); color: #fff; }
.hf-home-health h2, .hf-home-health .hf-home-eyebrow { color: #fff; }
.hf-home-health .hf-home-eyebrow { color: var(--hf-tan); }
.hf-home-health-intro { max-width: 720px; margin: 0 auto 40px; text-align: center; font-size: 18px; color: rgba(255,255,255,0.92); }
.hf-home-health h2 { text-align: center; margin-bottom: 16px; }
.hf-home-health-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 32px; }
.hf-home-health-card { background: #fff; color: var(--hf-text); border-radius: var(--hf-radius); padding: 28px; }
.hf-home-health-card h3 { font-size: 19px; margin-bottom: 8px; }
.hf-home-health-card p { font-size: 14px; color: var(--hf-muted); margin-bottom: 16px; }
.hf-home-health-cta-wrap { text-align: center; }
.hf-home-health .hf-home-btn-primary { background: var(--hf-tan); color: var(--hf-green-dark); }
.hf-home-health .hf-home-btn-primary:hover { background: #C29460; color: var(--hf-green-dark); }

/* ----- 6 + 7. Card grids (Gear / Latest) ----- */
.hf-home-cards-section h2 { margin-bottom: 32px; }
.hf-home-cards-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
.hf-home-card {
  background: #fff; border-radius: var(--hf-radius); overflow: hidden;
  box-shadow: var(--hf-card-shadow); display: flex; flex-direction: column;
  transition: transform .2s ease, box-shadow .2s ease;
}
.hf-home-card:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(31,31,27,0.10); }
.hf-home-card-img { aspect-ratio: 16/9; object-fit: cover; }
.hf-home-card-body { padding: 20px 22px 24px; display: flex; flex-direction: column; flex: 1; }
.hf-home-card h3 { font-size: 20px; margin-bottom: 8px; }
.hf-home-card-excerpt { color: var(--hf-muted); font-size: 14px; flex: 1; margin-bottom: 12px; }
.hf-home-card-link { font-size: 14px; font-weight: 600; }

/* ----- 8. Newsletter + Disclosure ----- */
.hf-home-newsletter { background: var(--hf-tan-soft); text-align: center; }
.hf-home-newsletter-inner { max-width: 720px; margin: 0 auto; }
.hf-home-newsletter h2 { margin-bottom: 12px; }
.hf-home-newsletter-sub { color: var(--hf-muted); margin-bottom: 28px; }
.hf-home-newsletter-form { display: flex; gap: 8px; justify-content: center; max-width: 480px; margin: 0 auto 16px; flex-wrap: wrap; }
.hf-home-newsletter-input {
  flex: 1; min-width: 240px; padding: 14px 18px; font-size: 15px;
  border: 1px solid var(--hf-border); border-radius: var(--hf-radius);
  font-family: 'Inter', sans-serif; background: #fff;
}
.hf-home-newsletter-input:focus { outline: 2px solid var(--hf-green); outline-offset: 1px; }
.hf-home-newsletter-disclosure { font-size: 13px; color: var(--hf-muted); margin-top: 24px; }
.hf-home-newsletter-disclosure a { color: var(--hf-muted); text-decoration: underline; }

/* ----- Mobile (≤ 820px) ----- */
@media (max-width: 820px) {
  .hf-home { font-size: 16px; }
  .hf-home h1 { font-size: 34px; }
  .hf-home h2 { font-size: 26px; }
  .hf-home h3 { font-size: 20px; }
  .hf-home-section { padding: 48px 0; }
  .hf-home-hero { padding: 56px 0 48px; }
  .hf-home-hero-grid,
  .hf-home-pillar-card,
  .hf-home-author-grid { grid-template-columns: 1fr; gap: 32px; }
  .hf-home-hero-photo,
  .hf-home-author-photo { margin: 0 auto; max-width: 240px; width: 240px; }
  .hf-home-topic-grid { grid-template-columns: repeat(2, 1fr); }
  .hf-home-cards-grid,
  .hf-home-health-cards { grid-template-columns: 1fr; }
}
@media (max-width: 480px) {
  .hf-home-topic-grid { grid-template-columns: 1fr; }
  .hf-home-newsletter-form { flex-direction: column; }
  .hf-home-newsletter-input { min-width: 0; }
}
```

- [ ] **Step 2: Validate the CSS file**

```bash
wc -l /Users/skitch/hf-homepage/homepage.css
python3 -c "
css = open('/Users/skitch/hf-homepage/homepage.css').read()
opens = css.count('{'); closes = css.count('}')
assert opens == closes, f'brace mismatch: {opens} open vs {closes} close'
print('CSS braces balanced')
"
```

Expected: brace count balanced.

---

## Task 6: Build section 1 — Hero

**Files:**
- Create: `/Users/skitch/hf-homepage/sections/01-hero.html`

- [ ] **Step 1: Write `01-hero.html` substituting `{{HERO_PHOTO}}` with the URL from `asset-manifest.json`**

Build the file with this template, then replace `{{HERO_PHOTO}}` with `manifest.hero_photo`:

```html
<section class="hf-home-section hf-home-hero">
  <div class="hf-home-container hf-home-hero-grid">
    <div>
      <span class="hf-home-eyebrow">Practical self-reliance</span>
      <h1>Real homesteading. From a mom who learned the hard way.</h1>
      <p class="hf-home-hero-sub">Written by Sarah Kate Wilder from her 12-acre Texas homestead. 83 field-tested guides on growing food, raising animals, off-grid living, and emergency preparedness.</p>
      <div class="hf-home-hero-ctas">
        <a class="hf-home-btn hf-home-btn-primary" href="https://homesteadfanatic.com/homesteading-skills-beginners/">Start Here</a>
        <a class="hf-home-btn hf-home-btn-outline" href="https://homesteadfanatic.com/about-2/">Read My Story</a>
      </div>
    </div>
    <div>
      <img class="hf-home-hero-photo" src="{{HERO_PHOTO}}" alt="Sarah Kate Wilder, founder of Homestead Fanatic" loading="eager" />
    </div>
  </div>
</section>
```

Substitution script:

```bash
python3 - <<'PY'
import json
m = json.load(open('/Users/skitch/hf-homepage/asset-manifest.json'))
tpl = """<section class="hf-home-section hf-home-hero">
  <div class="hf-home-container hf-home-hero-grid">
    <div>
      <span class="hf-home-eyebrow">Practical self-reliance</span>
      <h1>Real homesteading. From a mom who learned the hard way.</h1>
      <p class="hf-home-hero-sub">Written by Sarah Kate Wilder from her 12-acre Texas homestead. 83 field-tested guides on growing food, raising animals, off-grid living, and emergency preparedness.</p>
      <div class="hf-home-hero-ctas">
        <a class="hf-home-btn hf-home-btn-primary" href="https://homesteadfanatic.com/homesteading-skills-beginners/">Start Here</a>
        <a class="hf-home-btn hf-home-btn-outline" href="https://homesteadfanatic.com/about-2/">Read My Story</a>
      </div>
    </div>
    <div>
      <img class="hf-home-hero-photo" src="{{HERO_PHOTO}}" alt="Sarah Kate Wilder, founder of Homestead Fanatic" loading="eager" />
    </div>
  </div>
</section>"""
open('/Users/skitch/hf-homepage/sections/01-hero.html','w').write(tpl.replace("{{HERO_PHOTO}}", m['hero_photo']))
print('hero written')
PY
```

- [ ] **Step 2: Verify the file contains a real URL where `{{HERO_PHOTO}}` was**

```bash
grep -E 'src="https://[^"]+"' /Users/skitch/hf-homepage/sections/01-hero.html
```

Expected: shows the resolved URL.

---

## Task 7: Build section 2 — Featured Pillar

**Files:**
- Create: `/Users/skitch/hf-homepage/sections/02-pillar.html`

- [ ] **Step 1: Write `02-pillar.html` using `asset-manifest.pillar` data**

```bash
python3 - <<'PY'
import json
m = json.load(open('/Users/skitch/hf-homepage/asset-manifest.json'))
p = m['pillar']
html = f"""<section class="hf-home-section hf-home-pillar">
  <div class="hf-home-container">
    <div class="hf-home-pillar-card">
      <img class="hf-home-pillar-img" src="{p['image']}" alt="{p['title']}" loading="lazy" />
      <div>
        <span class="hf-home-eyebrow">Pillar guide</span>
        <h2>{p['title']}</h2>
        <p class="hf-home-pillar-excerpt">If you're just starting out — or just realized how dependent your family is on the systems around you — this is where to begin. Twenty-five concrete skills, with the order I'd learn them in if I were starting over.</p>
        <a class="read-more" href="{p['url']}">Read the guide →</a>
      </div>
    </div>
  </div>
</section>"""
open('/Users/skitch/hf-homepage/sections/02-pillar.html','w').write(html)
print('pillar written')
PY
```

- [ ] **Step 2: Verify**

```bash
grep -c 'hf-home-pillar' /Users/skitch/hf-homepage/sections/02-pillar.html
```

Expected: ≥ 4.

---

## Task 8: Build section 3 — Browse by Topic

**Files:**
- Create: `/Users/skitch/hf-homepage/sections/03-topics.html`

- [ ] **Step 1: Generate 6 topic tiles from `asset-manifest.topic_tiles`**

```bash
python3 - <<'PY'
import json
m = json.load(open('/Users/skitch/hf-homepage/asset-manifest.json'))
tiles_html = ""
for t in m['topic_tiles']:
    tiles_html += f"""    <div class="hf-home-topic-tile" style="background-image:url('{t['image']}')">
      <span class="hf-home-topic-tile-count">{t['count']} guides</span>
      <span class="hf-home-topic-tile-title">{t['name']}</span>
      <a href="{t['url']}" aria-label="{t['name']}"></a>
    </div>
"""
html = f"""<section class="hf-home-section hf-home-topics">
  <div class="hf-home-container">
    <span class="hf-home-eyebrow" style="display:block;text-align:center;">Browse by topic</span>
    <h2>What we cover</h2>
    <div class="hf-home-topic-grid">
{tiles_html}    </div>
  </div>
</section>"""
open('/Users/skitch/hf-homepage/sections/03-topics.html','w').write(html)
print('topics written, tiles:', len(m['topic_tiles']))
PY
```

Expected: `tiles: 6`.

- [ ] **Step 2: Verify**

```bash
grep -c 'hf-home-topic-tile"' /Users/skitch/hf-homepage/sections/03-topics.html
```

Expected: `6`.

---

## Task 9: Build section 4 — Author Block

**Files:**
- Create: `/Users/skitch/hf-homepage/sections/04-author.html`

- [ ] **Step 1: Write `04-author.html` using `asset-manifest.hero_photo` (same portrait)**

```bash
python3 - <<'PY'
import json
m = json.load(open('/Users/skitch/hf-homepage/asset-manifest.json'))
html = f"""<section class="hf-home-section hf-home-author">
  <div class="hf-home-container">
    <div class="hf-home-author-grid">
      <img class="hf-home-author-photo" src="{m['hero_photo']}" alt="Sarah Kate Wilder" loading="lazy" />
      <div>
        <span class="hf-home-eyebrow">About the author</span>
        <h2>Meet Sarah Kate.</h2>
        <p class="hf-home-author-bio">I'm a mom of three and the voice behind Homestead Fanatic. Five years ago I was a suburban mom in Texas with a Costco membership and zero homesteading skills. Then the 2021 ice storm hit — four days without power, heat, or running water with a newborn. That night changed everything. Today my family lives on 12 acres outside Wimberley, and this site is the resource I wish I'd had when I started.</p>
        <div class="hf-home-author-stats">
          <span class="hf-home-author-chip">12 acres</span>
          <span class="hf-home-author-chip">83 articles published</span>
          <span class="hf-home-author-chip">5 years homesteading</span>
          <span class="hf-home-author-chip">Mom of 3</span>
        </div>
        <a href="https://homesteadfanatic.com/about-2/" style="font-weight:600;">Read my full story →</a>
      </div>
    </div>
  </div>
</section>"""
open('/Users/skitch/hf-homepage/sections/04-author.html','w').write(html)
print('author written')
PY
```

- [ ] **Step 2: Verify**

```bash
grep -c 'hf-home-author-chip' /Users/skitch/hf-homepage/sections/04-author.html
```

Expected: `4`.

---

## Task 10: Build section 5 — Health Hub Callout

**Files:**
- Create: `/Users/skitch/hf-homepage/sections/05-health.html`

- [ ] **Step 1: Write `05-health.html`**

```bash
cat > /Users/skitch/hf-homepage/sections/05-health.html <<'HTML'
<section class="hf-home-section hf-home-health">
  <div class="hf-home-container">
    <span class="hf-home-eyebrow" style="display:block;text-align:center;">Health hub</span>
    <h2>The Natural Health Hub.</h2>
    <p class="hf-home-health-intro">When my doctor suggested $1,200/month GLP-1 injections after my third baby, I went looking for natural alternatives. What I found turned into the most-read content on this site.</p>
    <div class="hf-home-health-cards">
      <div class="hf-home-health-card">
        <span class="hf-home-eyebrow" style="color:var(--hf-green);">Pillar guide</span>
        <h3>The complete GLP-3 guide</h3>
        <p>What it is, how it works, and how it compares to prescription GLP-1s.</p>
        <a href="https://homesteadfanatic.com/glp3-the-complete-guide-to-natural-weight-management-for-homesteaders/" style="font-weight:600;">Read the guide →</a>
      </div>
      <div class="hf-home-health-card">
        <span class="hf-home-eyebrow" style="color:var(--hf-green);">Product review</span>
        <h3>GLP Three review</h3>
        <p>My honest take on the supplement I tried — what worked, what didn't.</p>
        <a href="https://homesteadfanatic.com/glp-three-review-a-natural-alternative-to-weight-loss-injections-for-homesteaders/" style="font-weight:600;">Read the review →</a>
      </div>
      <div class="hf-home-health-card">
        <span class="hf-home-eyebrow" style="color:var(--hf-green);">Buying guide</span>
        <h3>Where to buy GLP-3</h3>
        <p>How to spot quality products and avoid the knockoffs.</p>
        <a href="https://homesteadfanatic.com/where-to-buy-glp3-your-guide-to-finding-quality-products/" style="font-weight:600;">Read the guide →</a>
      </div>
    </div>
    <div class="hf-home-health-cta-wrap">
      <a class="hf-home-btn hf-home-btn-primary" href="https://homesteadfanatic.com/glp3-the-complete-guide-to-natural-weight-management-for-homesteaders/">Start with the GLP-3 guide</a>
    </div>
  </div>
</section>
HTML
```

- [ ] **Step 2: Verify**

```bash
grep -c 'hf-home-health-card' /Users/skitch/hf-homepage/sections/05-health.html
```

Expected: `4` (3 cards + the grid container).

---

## Task 11: Build section 6 — Latest Gear & Reviews

**Files:**
- Create: `/Users/skitch/hf-homepage/sections/06-gear.html`

- [ ] **Step 1: Render 3 gear cards from `dynamic-posts.json[gear]`**

```bash
python3 - <<'PY'
import json, html as html_lib
d = json.load(open('/Users/skitch/hf-homepage/dynamic-posts.json'))
cards = ""
for c in d['gear']:
    cards += f"""      <article class="hf-home-card">
        <a href="{c['url']}"><img class="hf-home-card-img" src="{c['image']}" alt="{html_lib.escape(c['image_alt'])}" loading="lazy" /></a>
        <div class="hf-home-card-body">
          <span class="hf-home-eyebrow">{c['eyebrow']}</span>
          <h3><a href="{c['url']}" style="color:inherit;">{c['title']}</a></h3>
          <p class="hf-home-card-excerpt">{html_lib.escape(c['excerpt'])}</p>
          <a class="hf-home-card-link" href="{c['url']}">Read review →</a>
        </div>
      </article>
"""
out = f"""<section class="hf-home-section hf-home-cards-section">
  <div class="hf-home-container">
    <span class="hf-home-eyebrow">Gear & reviews</span>
    <h2>The latest gear we've tested</h2>
    <div class="hf-home-cards-grid">
{cards}    </div>
  </div>
</section>"""
open('/Users/skitch/hf-homepage/sections/06-gear.html','w').write(out)
print('gear cards written:', len(d['gear']))
PY
```

Expected: `gear cards written: 3`.

- [ ] **Step 2: Verify**

```bash
grep -c 'class="hf-home-card"' /Users/skitch/hf-homepage/sections/06-gear.html
```

Expected: `3`.

---

## Task 12: Build section 7 — Latest Posts

**Files:**
- Create: `/Users/skitch/hf-homepage/sections/07-latest.html`

- [ ] **Step 1: Render 3 cards from `dynamic-posts.json[latest]`**

```bash
python3 - <<'PY'
import json, html as html_lib
d = json.load(open('/Users/skitch/hf-homepage/dynamic-posts.json'))
cards = ""
for c in d['latest']:
    cards += f"""      <article class="hf-home-card">
        <a href="{c['url']}"><img class="hf-home-card-img" src="{c['image']}" alt="{html_lib.escape(c['image_alt'])}" loading="lazy" /></a>
        <div class="hf-home-card-body">
          <span class="hf-home-eyebrow">{c['eyebrow']}</span>
          <h3><a href="{c['url']}" style="color:inherit;">{c['title']}</a></h3>
          <p class="hf-home-card-excerpt">{html_lib.escape(c['excerpt'])}</p>
          <a class="hf-home-card-link" href="{c['url']}">Read post →</a>
        </div>
      </article>
"""
out = f"""<section class="hf-home-section hf-home-cards-section" style="background:#fff;">
  <div class="hf-home-container">
    <span class="hf-home-eyebrow">Recently published</span>
    <h2>From the homestead</h2>
    <div class="hf-home-cards-grid">
{cards}    </div>
  </div>
</section>"""
open('/Users/skitch/hf-homepage/sections/07-latest.html','w').write(out)
print('latest cards written:', len(d['latest']))
PY
```

Expected: `latest cards written: 3`.

- [ ] **Step 2: Verify**

```bash
grep -c 'class="hf-home-card"' /Users/skitch/hf-homepage/sections/07-latest.html
```

Expected: `3`.

---

## Task 13: Build section 8 — Newsletter + Disclosure

**Files:**
- Create: `/Users/skitch/hf-homepage/sections/08-newsletter.html`

- [ ] **Step 1: Branch on `lc-form.json` — wire form action correctly**

```bash
python3 - <<'PY'
import json
lc = json.load(open('/Users/skitch/hf-homepage/lc-form.json'))
action = lc.get('action_url') or 'mailto:fred@konversly.com'
method = lc.get('method', 'POST').upper() if lc.get('action_url') else 'GET'
form_target = "" if lc.get('action_url') else 'target="_blank"'
note = "" if lc.get('action_url') else "<!-- LeadConnector endpoint not discovered; falling back to mailto. Replace action_url in lc-form.json and rebuild this section. -->"
html = f"""{note}
<section class="hf-home-section hf-home-newsletter">
  <div class="hf-home-container hf-home-newsletter-inner">
    <span class="hf-home-eyebrow">Stay in the loop</span>
    <h2>Get the homestead playbook.</h2>
    <p class="hf-home-newsletter-sub">Practical guides, gear reviews, and stories from the homestead. No spam, ever.</p>
    <form class="hf-home-newsletter-form" action="{action}" method="{method}" {form_target}>
      <input class="hf-home-newsletter-input" type="email" name="email" placeholder="your@email.com" required aria-label="Email address" />
      <button type="submit" class="hf-home-btn hf-home-btn-primary">Subscribe</button>
    </form>
    <p class="hf-home-newsletter-disclosure">Homestead Fanatic earns commission on some recommended products. Editorial picks come first. <a href="https://homesteadfanatic.com/affiliate-disclosure/">Read the full disclosure</a>.</p>
  </div>
</section>"""
open('/Users/skitch/hf-homepage/sections/08-newsletter.html','w').write(html)
print('newsletter written; form action:', action)
PY
```

- [ ] **Step 2: Verify**

```bash
grep 'action=' /Users/skitch/hf-homepage/sections/08-newsletter.html
```

Expected: shows the form action attribute.

---

## Task 14: Assemble + push to WP

**Files:**
- Create: `/Users/skitch/hf-homepage/homepage.html`
- Create: `/Users/skitch/hf-homepage/deploy-result.json`
- Modify: WP page ID 8 (remote)

- [ ] **Step 1: Concatenate CSS + 8 sections into one Gutenberg HTML block**

```bash
python3 - <<'PY'
css = open('/Users/skitch/hf-homepage/homepage.css').read()
parts = [open(f'/Users/skitch/hf-homepage/sections/{f}').read() for f in [
    '01-hero.html','02-pillar.html','03-topics.html','04-author.html',
    '05-health.html','06-gear.html','07-latest.html','08-newsletter.html'
]]
inner = "<style>\n" + css + "\n</style>\n<div class=\"hf-home\">\n" + "\n".join(parts) + "\n</div>"
content = "<!-- wp:html -->\n" + inner + "\n<!-- /wp:html -->"
open('/Users/skitch/hf-homepage/homepage.html','w').write(content)
print('homepage.html bytes:', len(content))
PY
```

Expected: prints a byte count > 10000.

- [ ] **Step 2: Push to page 8 via REST**

```bash
python3 - <<'PY'
import json, urllib.request, base64
auth = base64.b64encode(b"fred:Md7C 1cWk yhcX jmfs ffin lrZ6").decode()
content = open('/Users/skitch/hf-homepage/homepage.html').read()
req = urllib.request.Request(
    "https://homesteadfanatic.com/wp-json/wp/v2/pages/8",
    data=json.dumps({"content": content}).encode(),
    method="POST",
)
req.add_header("Authorization", f"Basic {auth}")
req.add_header("User-Agent", "Mozilla/5.0 (Macintosh)")
req.add_header("Content-Type", "application/json")
resp = urllib.request.urlopen(req)
result = json.loads(resp.read())
json.dump({"status": resp.status, "id": result["id"], "modified": result["modified"], "link": result["link"]}, open('/Users/skitch/hf-homepage/deploy-result.json','w'), indent=2)
print('DEPLOYED status=', resp.status, 'modified=', result['modified'])
PY
```

Expected: `DEPLOYED status= 200 modified= 2026-04-25T...`.

---

## Task 15: Verify on live site

**Why:** Catch broken layouts, broken links, and form failure before declaring done.

- [ ] **Step 1: Cache-bust + fetch the rendered homepage**

```bash
curl -s -H "User-Agent: $UA" "https://homesteadfanatic.com/?v=$(date +%s)" > /tmp/hf_after.html
wc -c /tmp/hf_after.html
grep -c 'class="hf-home' /tmp/hf_after.html
```

Expected: file size > 50KB; class count > 20.

- [ ] **Step 2: Scan for broken section URLs (no 404s among the links we added)**

```bash
python3 - <<'PY'
import re, urllib.request
html = open('/tmp/hf_after.html').read()
# extract our internal links
urls = sorted(set(re.findall(r'href="(https://homesteadfanatic\.com/[^"#?]+)"', html)))
bad = []
for u in urls[:30]:
    try:
        req = urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0 (Macintosh)"})
        code = urllib.request.urlopen(req, timeout=10).status
        if code >= 400: bad.append((u, code))
    except urllib.error.HTTPError as e:
        bad.append((u, e.code))
    except Exception as e:
        bad.append((u, str(e)))
print('checked:', len(urls[:30]), 'bad:', bad)
PY
```

Expected: `bad: []`.

- [ ] **Step 3: Visually verify in a browser at three widths**

Open in browser:
- Desktop (1440px): https://homesteadfanatic.com/
- Tablet (768px): use browser devtools responsive mode
- Mobile (375px): use browser devtools responsive mode

Confirm at each width:
- Hero photo and copy don't overlap
- Topic tiles are 3 cols / 2 cols / 1 col
- Author photo is round
- Health hub band is solid green with white text
- Card grids reflow to 1 col on mobile
- Newsletter form button doesn't overflow

- [ ] **Step 4: Test the email capture form**

Submit the form on the live homepage with a test email (use `homepage-test+$(date +%s)@konversly.com`). Then check:
- If LC endpoint was discovered: confirm the lead appears in LeadConnector dashboard within 1 minute.
- If fallback (mailto) was used: confirm the email opens correctly. Note in `deploy-result.json` that LC was not wired and create a follow-up todo to find the endpoint.

- [ ] **Step 5: Browser console check**

In DevTools console, look for any red errors. Acceptable warnings: font-loading, deprecated APIs from other plugins. Not acceptable: 404s on assets we added (hero photo, topic tile images), CSS parse errors.

If any error refers to a URL we added: re-check `asset-manifest.json` and re-run the affected section task.

---

## Task 16: Commit local artifacts to git

**Why:** The home directory is a git repo. Track the spec, plan, backup, and final HTML so the work is reversible from history.

**Files:**
- Modify: home directory git index

- [ ] **Step 1: Stage the specific files (avoid -A in this very large dirty home dir)**

```bash
git add /Users/skitch/homesteadfanatic-homepage-redesign-spec.md
git add /Users/skitch/homesteadfanatic-homepage-redesign-plan.md
git add /Users/skitch/hf-homepage/
```

- [ ] **Step 2: Confirm what's staged**

```bash
git status --short | grep -E 'homesteadfanatic|hf-homepage' | head -30
```

Expected: shows the 4 docs + the `hf-homepage/` artifacts staged.

- [ ] **Step 3: Commit**

```bash
git commit -m "$(cat <<'EOF'
Add Homestead Fanatic homepage redesign — spec, plan, build artifacts

Hybrid editorial+warmth design pushed to homesteadfanatic.com page ID 8 via WP REST API.
Includes: design spec, implementation plan, full backup of original homepage, asset manifest,
8 section HTML files, namespaced CSS, and final assembled homepage payload.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Expected: one commit created.

---

## Acceptance Criteria (recap from spec)

Before declaring this plan complete:

- [ ] Homepage renders correctly at 1440px, 1024px, 768px, 375px
- [ ] All 8 sections present in correct order
- [ ] No 404s among the links we added (Task 15 step 2 returns `bad: []`)
- [ ] Newsletter form submits without console error
- [ ] LeadConnector lead recorded (or LC fallback documented in `deploy-result.json`)
- [ ] No console errors referencing our added assets
- [ ] Backup file exists and `REVERT.sh` works (test by cat'ing it; do not actually revert)
- [ ] All artifacts committed to git

---

## Reversibility

If anything looks wrong post-deploy:

```bash
bash /Users/skitch/hf-homepage/REVERT.sh
```

This re-pushes the original `content.raw` back to page 8. Revert time: ~3 seconds.
