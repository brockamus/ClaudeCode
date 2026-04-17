"""Validate JSON-LD schema output against schema.org conventions."""
import json
import re
import sys


REQUIRED_GRAPH_TYPES_COLLECTION = {"Organization", "WebSite", "BreadcrumbList", "CollectionPage"}
REQUIRED_GRAPH_TYPES_PRODUCT = {"Organization", "WebSite", "BreadcrumbList", "Product"}
REQUIRED_GRAPH_TYPES_ARTICLE = {"Organization", "WebSite", "BreadcrumbList", "Article"}


def extract_jsonld(html):
    """Extract all JSON-LD blocks from a page of HTML."""
    blocks = re.findall(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>\s*(.*?)\s*</script>',
        html,
        flags=re.DOTALL,
    )
    parsed = []
    for b in blocks:
        try:
            parsed.append(json.loads(b))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON-LD: {e}\n{b[:300]}")
    return parsed


def assert_valid_graph(jsonld, required_types):
    if "@graph" not in jsonld:
        raise AssertionError(f"JSON-LD missing @graph node")
    graph = jsonld["@graph"]
    types = {n.get("@type") for n in graph if isinstance(n.get("@type"), str)}
    types.update(t for n in graph if isinstance(n.get("@type"), list) for t in n["@type"])
    missing = required_types - types
    if missing:
        raise AssertionError(f"Graph missing required types: {missing}. Present: {types}")
    for n in graph:
        if "@id" not in n and n.get("@type") not in ("BreadcrumbList",):
            raise AssertionError(f"Node {n.get('@type')} missing @id for graph cross-referencing")


def validate_collection_page(html):
    blocks = extract_jsonld(html)
    # Find the single @graph block
    graphs = [b for b in blocks if "@graph" in b]
    if len(graphs) != 1:
        raise AssertionError(f"Expected exactly 1 @graph block, found {len(graphs)}")
    assert_valid_graph(graphs[0], REQUIRED_GRAPH_TYPES_COLLECTION)
    return True


def validate_product_page(html):
    blocks = extract_jsonld(html)
    graphs = [b for b in blocks if "@graph" in b]
    if len(graphs) != 1:
        raise AssertionError(f"Expected exactly 1 @graph block, found {len(graphs)}")
    assert_valid_graph(graphs[0], REQUIRED_GRAPH_TYPES_PRODUCT)
    return True


def validate_article_page(html):
    blocks = extract_jsonld(html)
    graphs = [b for b in blocks if "@graph" in b]
    if len(graphs) != 1:
        raise AssertionError(f"Expected exactly 1 @graph block, found {len(graphs)}")
    assert_valid_graph(graphs[0], REQUIRED_GRAPH_TYPES_ARTICLE)
    return True


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python schema_validator.py <collection|product|article> <url_or_file>")
        sys.exit(2)
    kind = sys.argv[1]
    src = sys.argv[2]
    if src.startswith("http"):
        import urllib.request
        html = urllib.request.urlopen(src).read().decode("utf-8", errors="replace")
    else:
        html = open(src, encoding="utf-8").read()
    if kind == "collection":
        validate_collection_page(html)
    elif kind == "product":
        validate_product_page(html)
    elif kind == "article":
        validate_article_page(html)
    print(f"OK: {src} passes {kind} schema validation.")
