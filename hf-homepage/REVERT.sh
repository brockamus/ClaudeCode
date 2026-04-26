#!/usr/bin/env bash
# Emergency revert: re-push original homepage content (backup-page-8-2026-04-25.html) to WP page ID 8.
# Run with: bash /Users/skitch/hf-homepage/REVERT.sh
set -e
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
