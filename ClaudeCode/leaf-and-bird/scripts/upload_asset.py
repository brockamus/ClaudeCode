"""Upload a local file to the live Shopify theme."""
import sys
import pathlib
import shopify_api

LIVE_THEME_ID = 186951631147  # "Copy of Konversly-1-5-1-skincare-2" (published 2026-04-16)


def upload(local_path, asset_key):
    content = pathlib.Path(local_path).read_text(encoding="utf-8")
    body = {"asset": {"key": asset_key, "value": content}}
    resp = shopify_api.put(f"/themes/{LIVE_THEME_ID}/assets.json", body)
    print(f"Uploaded {local_path} → {asset_key}")
    return resp


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python upload_asset.py <local_file> <asset_key>")
        sys.exit(2)
    upload(sys.argv[1], sys.argv[2])
