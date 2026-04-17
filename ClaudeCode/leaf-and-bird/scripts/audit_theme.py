"""Audit the locally-backed-up theme for common SEO issues."""
import pathlib
import re
import json

THEME_DIR = pathlib.Path(__file__).resolve().parent.parent / "theme-backup"


def read(path):
    p = THEME_DIR / path
    return p.read_text(encoding="utf-8") if p.exists() else ""


def find_patterns(pattern, file_glob, flags=0):
    hits = []
    for path in THEME_DIR.rglob(file_glob):
        rel = path.relative_to(THEME_DIR)
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        for m in re.finditer(pattern, text, flags):
            line_no = text[: m.start()].count("\n") + 1
            hits.append((str(rel), line_no, m.group(0)[:200]))
    return hits


def main():
    report = ["# Leaf & Bird Theme SEO Audit\n"]

    report.append("## 1. Organization schema occurrences")
    for hit in find_patterns(r'"@type"\s*:\s*"Organization"', "*.liquid"):
        report.append(f"- `{hit[0]}:{hit[1]}` — `{hit[2]}`")
    report.append("")

    report.append("## 2. Product schema occurrences")
    for hit in find_patterns(r'"@type"\s*:\s*"Product"', "*.liquid"):
        report.append(f"- `{hit[0]}:{hit[1]}` — `{hit[2]}`")
    report.append("")

    report.append("## 3. WebSite schema occurrences")
    for hit in find_patterns(r'"@type"\s*:\s*"WebSite"', "*.liquid"):
        report.append(f"- `{hit[0]}:{hit[1]}` — `{hit[2]}`")
    report.append("")

    report.append("## 4. H1 usages in theme")
    for hit in find_patterns(r"<h1[\s>]", "*.liquid", re.IGNORECASE):
        report.append(f"- `{hit[0]}:{hit[1]}` — `{hit[2]}`")
    report.append("")

    report.append("## 5. Logo-in-header patterns (possible H1 abuse)")
    for hit in find_patterns(r"header.*logo|logo.*h1|h1.*logo", "*.liquid", re.IGNORECASE | re.DOTALL):
        report.append(f"- `{hit[0]}:{hit[1]}`")
    report.append("")

    report.append("## 6. OG image tags (check for http:// instead of https://)")
    for hit in find_patterns(r'property="og:image"[^>]*http://', "*.liquid"):
        report.append(f"- HTTP OG image: `{hit[0]}:{hit[1]}` — `{hit[2]}`")
    report.append("")

    report.append("## 7. Canonical tag references")
    for hit in find_patterns(r'rel="canonical"', "*.liquid"):
        report.append(f"- `{hit[0]}:{hit[1]}` — `{hit[2]}`")
    report.append("")

    report.append("## 8. robots meta / noindex")
    for hit in find_patterns(r'name="robots"|noindex', "*.liquid", re.IGNORECASE):
        report.append(f"- `{hit[0]}:{hit[1]}` — `{hit[2]}`")
    report.append("")

    report.append("## 9. Image alt attribute usage")
    imgs_with_alt = find_patterns(r"<img[^>]*\balt=", "*.liquid", re.IGNORECASE)
    imgs_all = find_patterns(r"<img\b", "*.liquid", re.IGNORECASE)
    report.append(f"- Total `<img` tags: {len(imgs_all)}")
    report.append(f"- With `alt=`: {len(imgs_with_alt)}")
    report.append(f"- Missing alt: {len(imgs_all) - len(imgs_with_alt)}")
    report.append("")

    report.append("## 10. Meta description usages")
    for hit in find_patterns(r'name="description"', "*.liquid"):
        report.append(f"- `{hit[0]}:{hit[1]}` — `{hit[2]}`")
    report.append("")

    report.append("## 11. Existing FAQPage schema")
    for hit in find_patterns(r'"@type"\s*:\s*"FAQPage"', "*.liquid"):
        report.append(f"- `{hit[0]}:{hit[1]}` — `{hit[2]}`")
    report.append("")

    out = pathlib.Path(__file__).resolve().parent.parent / "content" / "theme-audit-report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(report), encoding="utf-8")
    print(f"Report written to {out}")


if __name__ == "__main__":
    main()
