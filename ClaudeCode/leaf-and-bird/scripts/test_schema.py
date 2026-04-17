"""Tests for the schema validator — run before writing the Liquid snippet."""
import json
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from schema_validator import extract_jsonld, assert_valid_graph, validate_collection_page


def test_extract_jsonld_finds_blocks():
    html = '''<html><head>
    <script type="application/ld+json">{"@type":"Organization","name":"x"}</script>
    </head></html>'''
    blocks = extract_jsonld(html)
    assert len(blocks) == 1
    assert blocks[0]["name"] == "x"


def test_assert_valid_graph_passes_minimum():
    g = {"@graph": [
        {"@type": "Organization", "@id": "#org"},
        {"@type": "WebSite", "@id": "#site"},
        {"@type": "BreadcrumbList"},
        {"@type": "CollectionPage", "@id": "#page"},
    ]}
    assert_valid_graph(g, {"Organization", "WebSite", "BreadcrumbList", "CollectionPage"})


def test_assert_valid_graph_fails_missing_type():
    g = {"@graph": [{"@type": "Organization", "@id": "#org"}]}
    try:
        assert_valid_graph(g, {"Organization", "WebSite"})
    except AssertionError as e:
        assert "WebSite" in str(e)
        return
    raise AssertionError("should have raised")


def test_validate_collection_page_rejects_empty():
    try:
        validate_collection_page("<html></html>")
    except AssertionError:
        return
    raise AssertionError("should have raised")


if __name__ == "__main__":
    test_extract_jsonld_finds_blocks()
    test_assert_valid_graph_passes_minimum()
    test_assert_valid_graph_fails_missing_type()
    test_validate_collection_page_rejects_empty()
    print("All schema validator tests passed.")
