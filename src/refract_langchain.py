"""
LangChain document loader for Refract.

Loads Refract events as LangChain Documents, where each event becomes a
Document with the event text as content and stability metadata in metadata.

Requires: refract-py, langchain-core

Usage:
    from refract_langchain import RefractLoader

    loader = RefractLoader(page="Bitcoin", depth="forensic")
    docs = loader.load()

    for doc in docs:
        print(doc.page_content[:100], doc.metadata["event_type"], doc.metadata["stability_score"])
"""

from typing import Iterator, Optional

from langchain_core.documents import Document
from langchain_core.document_loaders import BaseLoader
from refract import Refract


class RefractLoader(BaseLoader):
    """Load Refract analysis results as LangChain Documents.

    Each event becomes a Document. The event text (before/after) is the
    page content. Provenance metadata (event type, revision range, analyzer
    name/version, schema version) is stored in metadata.

    Args:
        page: Wikipedia page title.
        depth: Analysis depth (brief, detailed, forensic).
        api_url: MediaWiki API URL (default: English Wikipedia).
        min_stability: Minimum stability score (0-1) to include. Events
            with high revert counts, citation churn, or edit clusters
            score lower. Default 0 (include all).
    """

    def __init__(
        self,
        page: str,
        depth: str = "detailed",
        api_url: Optional[str] = None,
        min_stability: float = 0.0,
    ):
        self.page = page
        self.depth = depth
        self.api_url = api_url
        self.min_stability = min_stability
        self._client = Refract()

    def _compute_stability(self, events: list) -> dict[str, float]:
        scores: dict[str, list[float]] = {}
        for e in events:
            cid = e.get("claimId") or e.get("eventType", "") + "_" + str(e.get("toRevisionId", 0))
            scores.setdefault(cid, [])
            base = 0.8
            if e.get("eventType") in ("revert_detected", "edit_cluster_detected"):
                base = 0.2
            elif e.get("eventType") == "sentence_removed":
                base = 0.0
            elif e.get("eventType") == "sentence_modified":
                base = 0.5
            elif e.get("eventType") == "sentence_first_seen":
                base = 0.9
            scores[cid].append(base)
        return {cid: sum(v) / len(v) for cid, v in scores.items()}

    def lazy_load(self) -> Iterator[Document]:
        events = self._client.export(self.page, format="ndjson")
        stability = self._compute_stability(events)

        for e in events:
            fact = (e.get("deterministicFacts") or [None])[0]
            cid = e.get("claimId") or e.get("eventType", "") + "_" + str(e.get("toRevisionId", 0))
            score = stability.get(cid, 0.5)
            if score < self.min_stability:
                continue

            content = e.get("after") or e.get("before") or e.get("eventType", "")
            metadata = {
                "source": f"wikipedia/{self.page}",
                "event_type": e.get("eventType"),
                "from_revision_id": e.get("fromRevisionId"),
                "to_revision_id": e.get("toRevisionId"),
                "section": e.get("section", ""),
                "timestamp": e.get("timestamp"),
                "schema_version": e.get("schemaVersion"),
                "analyzer": fact.get("provenance", {}).get("analyzer") if fact else None,
                "analyzer_version": fact.get("provenance", {}).get("version") if fact else None,
                "stability_score": round(score, 3),
                "layer": e.get("layer"),
                "claim_id": cid,
            }
            yield Document(page_content=content, metadata=metadata)
