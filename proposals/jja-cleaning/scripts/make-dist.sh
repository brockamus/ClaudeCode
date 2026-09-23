#!/usr/bin/env bash
# Assembles dist/ for Cloudflare Pages: the site lives under /jja-cleaning/,
# with Pages-level headers, redirects, robots and 404 at the root.
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf dist && mkdir -p dist/jja-cleaning
cp -R site/. dist/jja-cleaning/
rm -f dist/jja-cleaning/.htaccess dist/jja-cleaning/robots.txt
cp cloudflare/_headers cloudflare/_redirects cloudflare/robots.txt cloudflare/404.html dist/
echo "dist/ ready: $(find dist -type f | wc -l) files"
