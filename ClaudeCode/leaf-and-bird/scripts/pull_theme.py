"""Pull all files from the live Shopify theme to a local directory."""
import os
import sys
import pathlib
import shopify_api

LIVE_THEME_ID = 186309509419  # Konversly-1-5-1-skincare-2 (confirmed live in spec)
OUT_DIR = pathlib.Path(__file__).resolve().parent.parent / "theme-backup"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    assets = shopify_api.get(f"/themes/{LIVE_THEME_ID}/assets.json")["assets"]
    print(f"Found {len(assets)} assets. Downloading...")
    for asset in assets:
        key = asset["key"]
        detail = shopify_api.get(f"/themes/{LIVE_THEME_ID}/assets.json", params={"asset[key]": key})["asset"]
        dest = OUT_DIR / key
        dest.parent.mkdir(parents=True, exist_ok=True)
        if "value" in detail:
            dest.write_text(detail["value"], encoding="utf-8")
        elif "attachment" in detail:
            import base64
            dest.write_bytes(base64.b64decode(detail["attachment"]))
        print(f"  {key}")
    print(f"Done. {len(assets)} files in {OUT_DIR}")


if __name__ == "__main__":
    main()
