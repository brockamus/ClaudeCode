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
