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
