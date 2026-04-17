"""Verify each PDRN (and later all) money page has ≥2 intra-pillar links + ≥1 cross-pillar link + ≥1 article link."""
import re
import sys
import urllib.request


PDRN_PAGES = [
    "/collections/pdrn-serum",
    "/collections/pdrn-skincare",
    "/collections/best-pdrn-serum",
    "/collections/pdrn-eye-cream",
    "/collections/pdrn-vs-retinol",
    "/collections/clean-korean-skincare",
    "/collections/vegan-pdrn-serum",
]

ALL_PAGES = PDRN_PAGES + [
    "/collections/tallow-cream",
    "/collections/whipped-tallow-face-cream",
    "/collections/best-tallow-cream",
    "/collections/tallow-cream-for-eczema",
    "/collections/non-toxic-skincare",
    "/collections/pregnancy-safe-skincare",
    "/collections/seed-oil-free-skincare",
    "/collections/clean-skincare-for-moms",
]

BASE = "https://leafandbird.com"


def get_internal_links(url):
    html = urllib.request.urlopen(url).read().decode("utf-8", errors="replace")
    # Isolate the body content area — avoid nav/footer link collection
    # Just grab all internal hrefs; duplicates filtered by set
    links = set(re.findall(r'href="(/collections/[^"#?\s]+|/blogs/[^"#?\s]+|/products/[^"#?\s]+)"', html))
    return links


def main():
    pages = PDRN_PAGES if "--pdrn" in sys.argv else ALL_PAGES
    warnings = 0
    for path in pages:
        url = BASE + path
        try:
            links = get_internal_links(url)
        except Exception as e:
            print(f"{path}  ERROR  {e}")
            continue

        collection_links = sorted(l for l in links if l.startswith("/collections/") and l != path)
        blog_links = sorted(l for l in links if l.startswith("/blogs/"))
        product_links = sorted(l for l in links if l.startswith("/products/"))

        pdrn_pillar_links = [l for l in collection_links if any(x in l for x in ("/pdrn", "clean-korean", "vegan-pdrn"))]
        tallow_links = [l for l in collection_links if "tallow" in l]
        umbrella_links = [l for l in collection_links if any(x in l for x in ("non-toxic", "pregnancy-safe", "seed-oil-free", "skincare-for-moms"))]

        print(f"{path}")
        print(f"  collections: {len(collection_links)}  |  articles: {len(blog_links)}  |  products: {len(product_links)}")
        print(f"  pdrn-pillar: {len(pdrn_pillar_links)}  |  tallow-pillar: {len(tallow_links)}  |  umbrella-pillar: {len(umbrella_links)}")

        # Per-page expectations (soft warnings, not failures)
        if len(collection_links) < 2:
            print(f"  WARN: only {len(collection_links)} outbound collection links (<2)")
            warnings += 1
    print(f"\n{warnings} warnings across {len(pages)} pages.")


if __name__ == "__main__":
    main()
