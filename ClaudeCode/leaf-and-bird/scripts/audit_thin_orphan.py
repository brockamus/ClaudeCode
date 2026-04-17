"""Flag thin pages (<400 words of body content) and orphan pages (0 inbound internal links).

Thin-page metric: strips scripts/styles/nav/footer, counts remaining words on main content.
Orphan metric: for each tracked URL, count how many OTHER tracked URLs link to it via <a href>.
"""
import re
import sys
import urllib.request
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from site_sanity import URLS

HOST = "leafandbird.com"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "LB-Audit/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="ignore")


def word_count(html):
    # Strip script/style/nav/footer blocks.
    for tag in ("script", "style", "nav", "footer", "header", "aside"):
        html = re.sub(rf"<{tag}\b[^>]*>.*?</{tag}>", " ", html, flags=re.S | re.I)
    # Strip remaining tags.
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"&[a-z]+;", " ", text)
    return len(text.split())


def inbound_link_count(target_path, pages):
    """Count how many pages link to target_path."""
    count = 0
    linkers = []
    for page_url, html in pages.items():
        if page_url.endswith(target_path):
            continue
        # Look for hrefs matching the target_path.
        pattern = re.compile(rf'href=["\'][^"\']*{re.escape(target_path)}[/?#"\']', re.I)
        if pattern.search(html):
            count += 1
            linkers.append(page_url.replace(f"https://{HOST}", ""))
    return count, linkers


def main():
    pages = {}
    print("Fetching URLs...")
    for _, url in URLS:
        try:
            pages[url] = fetch(url)
        except Exception as e:
            print(f"  ERROR {url}: {e}")

    print(f"\n==> Thin-page check ({len(pages)} URLs, threshold 400 words)")
    thin = []
    for url, html in pages.items():
        wc = word_count(html)
        marker = "THIN" if wc < 400 else "ok  "
        if wc < 400:
            thin.append((url, wc))
        print(f"  {marker}  {wc:>5}  {url}")
    if thin:
        print(f"\n  {len(thin)} thin page(s) flagged.")

    print(f"\n==> Orphan-page check (0 inbound links from other tracked URLs)")
    orphans = []
    for url, _ in pages.items():
        target_path = url.replace(f"https://{HOST}", "")
        count, linkers = inbound_link_count(target_path, pages)
        marker = "ORPHAN" if count == 0 else f"in={count:>2}"
        if count == 0:
            orphans.append(url)
        print(f"  {marker}  {url}")
    if orphans:
        print(f"\n  {len(orphans)} orphan page(s) flagged.")

    if thin or orphans:
        sys.exit(1)
    print("\n==> All pages pass thin + orphan checks.")


if __name__ == "__main__":
    main()
