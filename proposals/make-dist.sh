#!/usr/bin/env bash
# Assembles dist/ for the konversly-proposals Cloudflare Pages project.
# Each proposal is a folder; Pages-level config lives in _pages/.
set -euo pipefail
cd "$(dirname "$0")"
rm -rf dist && mkdir -p dist
cp -R jja-cleaning/site dist/jja-cleaning
rm -f dist/jja-cleaning/.htaccess dist/jja-cleaning/robots.txt
cp -R website dist/website
cp _pages/_headers _pages/_redirects _pages/robots.txt _pages/404.html dist/
echo "dist/ ready: $(find dist -type f | wc -l) files"
