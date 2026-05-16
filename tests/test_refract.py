"""Tests for refract-py."""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from refract import Refract, EvidenceEvent, DeterministicFact


def test_parse_event():
    """Test that a raw dict is correctly parsed into typed objects."""
    raw = {
        "eventType": "revert_detected",
        "schemaVersion": "0.4.0",
        "fromRevisionId": 100,
        "toRevisionId": 101,
        "section": "",
        "before": "",
        "after": "revert vandalism",
        "timestamp": "2026-01-01T00:00:00Z",
        "layer": "observed",
        "deterministicFacts": [
            {
                "fact": "revert_detected",
                "detail": "comment=revert vandalism",
                "provenance": {
                    "analyzer": "revert-detector",
                    "version": "0.4.0",
                    "inputHashes": [],
                },
            }
        ],
    }
    from refract import _parse_event
    event = _parse_event(raw)
    assert event.eventType == "revert_detected"
    assert event.schemaVersion == "0.4.0"
    assert event.fromRevisionId == 100
    assert len(event.deterministicFacts) == 1
    assert event.deterministicFacts[0].fact == "revert_detected"
    assert event.deterministicFacts[0].provenance.analyzer == "revert-detector"


def test_flatten():
    """Test that flatten_event produces the correct flat dict."""
    from refract import _parse_event, _flatten_event
    event = _parse_event({
        "eventType": "citation_added",
        "schemaVersion": "0.4.0",
        "fromRevisionId": 10,
        "toRevisionId": 11,
        "section": "body",
        "before": "",
        "after": "https://example.com",
        "timestamp": "2026-01-01T00:00:00Z",
        "layer": "observed",
        "deterministicFacts": [
            {
                "fact": "citation_changed",
                "detail": "type=added",
                "provenance": {
                    "analyzer": "citation-tracker",
                    "version": "0.4.0",
                    "inputHashes": [],
                },
            }
        ],
    })
    flat = _flatten_event(event)
    assert flat["event_type"] == "citation_added"
    assert flat["fact"] == "citation_changed"
    assert flat["analyzer_name"] == "citation-tracker"


def test_truthy():
    """Placeholder for CLI integration tests (requires refract CLI installed)."""
    assert True
