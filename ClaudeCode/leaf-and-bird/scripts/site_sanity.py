"""Crawl the 24 new Leaf & Bird URLs and run a battery of SEO/schema checks."""
import re
import sys
import urllib.request
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from schema_validator import validate_collection_page, validate_article_page

URLS = [
    # 15 money pages
    ("collection", "https://leafandbird.com/collections/pdrn-serum"),
    ("collection", "https://leafandbird.com/collections/pdrn-skincare"),
    ("collection", "https://leafandbird.com/collections/best-pdrn-serum"),
    ("collection", "https://leafandbird.com/collections/pdrn-eye-cream"),
    ("collection", "https://leafandbird.com/collections/pdrn-vs-retinol"),
    ("collection", "https://leafandbird.com/collections/clean-korean-skincare"),
    ("collection", "https://leafandbird.com/collections/vegan-pdrn-serum"),
    ("collection", "https://leafandbird.com/collections/tallow-cream"),
    ("collection", "https://leafandbird.com/collections/whipped-tallow-face-cream"),
    ("collection", "https://leafandbird.com/collections/best-tallow-cream"),
    ("collection", "https://leafandbird.com/collections/tallow-cream-for-eczema"),
    ("collection", "https://leafandbird.com/collections/non-toxic-skincare"),
    ("collection", "https://leafandbird.com/collections/pregnancy-safe-skincare"),
    ("collection", "https://leafandbird.com/collections/seed-oil-free-skincare"),
    ("collection", "https://leafandbird.com/collections/clean-skincare-for-moms"),
    # 9 articles
    ("article", "https://leafandbird.com/blogs/journal/what-is-pdrn-complete-guide"),
    ("article", "https://leafandbird.com/blogs/journal/is-pdrn-salmon-sperm"),
    ("article", "https://leafandbird.com/blogs/journal/pdrn-vs-retinol"),
    ("article", "https://leafandbird.com/blogs/journal/pdrn-benefits-for-skin"),
    ("article", "https://leafandbird.com/blogs/journal/how-to-make-tallow-face-cream"),
    ("article", "https://leafandbird.com/blogs/journal/beef-tallow-for-skin-guide"),
    ("article", "https://leafandbird.com/blogs/journal/pregnancy-safe-skincare-guide"),
    ("article", "https://leafandbird.com/blogs/journal/is-korean-skincare-non-toxic"),
    ("article", "https://leafandbird.com/blogs/journal/is-pdrn-vegan"),
]


def checks_for(kind, url):
    try:
        html = urllib.request.urlopen(url, timeout=20).read().decode("utf-8", errors="replace")
    except Exception as e:
        return [f"fetch failed: {e}"]
    probs = []
    try:
        if kind == "collection":
            validate_collection_page(html)
        elif kind == "article":
            validate_article_page(html)
    except Exception as e:
        probs.append(f"schema: {e}")
    h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.DOTALL | re.IGNORECASE)
    if len(h1s) < 1:
        probs.append(f"h1 count = {len(h1s)} (expected ≥1)")
    if not re.search(r'<meta name="description" content="[^"]{20,}"', html):
        probs.append("missing or short meta description")
    if not re.search(r'rel="canonical"[^>]+href="[^"]+"', html):
        probs.append("missing canonical")
    if re.search(r'property="og:image"[^>]+content="http://', html):
        probs.append("og:image is http://")
    collection_links = set(re.findall(r'href="(/collections/[^"#?]+)"', html))
    if len(collection_links) < 2:
        probs.append(f"only {len(collection_links)} internal collection links")
    if not re.search(r'"@type":\s*"FAQPage"', html):
        probs.append("no FAQPage schema")
    return probs


def main():
    any_problems = False
    for kind, url in URLS:
        probs = checks_for(kind, url)
        status = "OK" if not probs else "ISSUES"
        print(f"{status:8}  {url}")
        for p in probs:
            print(f"          - {p}")
            any_problems = True
    if any_problems:
        print("\n==> Some checks failed.")
        sys.exit(1)
    print("\n==> All 24 URLs pass sanity checks.")


if __name__ == "__main__":
    main()
