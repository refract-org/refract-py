"""
Python SDK for Refract — wraps the Refract CLI via subprocess.
"""

import json
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import Any

__all__ = ["Refract", "EvidenceEvent", "DeterministicFact", "FactProvenance"]


@dataclass
class FactProvenance:
    analyzer: str | None = None
    version: str | None = None
    inputHashes: list[str] | None = None
    parameters: dict[str, Any] | None = None


@dataclass
class DeterministicFact:
    fact: str = ""
    detail: str | None = None
    provenance: FactProvenance | None = None


@dataclass
class EvidenceEvent:
    schemaVersion: str | None = None
    eventId: str | None = None
    eventType: str = ""
    fromRevisionId: int = 0
    toRevisionId: int = 0
    section: str = ""
    before: str = ""
    after: str = ""
    deterministicFacts: list[DeterministicFact] = field(default_factory=list)
    modelInterpretation: dict | None = None
    layer: str = ""
    timestamp: str = ""


def _parse_event(obj: dict) -> EvidenceEvent:
    facts = []
    for f in obj.get("deterministicFacts", []):
        prov = f.get("provenance")
        provenance = FactProvenance(
            analyzer=prov.get("analyzer") if prov else None,
            version=prov.get("version") if prov else None,
            inputHashes=prov.get("inputHashes") if prov else None,
            parameters=prov.get("parameters") if prov else None,
        ) if prov else None
        facts.append(DeterministicFact(
            fact=f.get("fact", ""),
            detail=f.get("detail"),
            provenance=provenance,
        ))
    return EvidenceEvent(
        schemaVersion=obj.get("schemaVersion"),
        eventId=obj.get("eventId"),
        eventType=obj.get("eventType", ""),
        fromRevisionId=obj.get("fromRevisionId", 0),
        toRevisionId=obj.get("toRevisionId", 0),
        section=obj.get("section", ""),
        before=obj.get("before", ""),
        after=obj.get("after", ""),
        deterministicFacts=facts,
        modelInterpretation=obj.get("modelInterpretation"),
        layer=obj.get("layer", ""),
        timestamp=obj.get("timestamp", ""),
    )


def _flatten_event(e: EvidenceEvent) -> dict[str, Any]:
    fact = e.deterministicFacts[0] if e.deterministicFacts else None
    return {
        "timestamp": e.timestamp,
        "event_type": e.eventType,
        "from_revision_id": e.fromRevisionId,
        "to_revision_id": e.toRevisionId,
        "section": e.section,
        "event_id": e.eventId or "",
        "schema_version": e.schemaVersion or "",
        "layer": e.layer,
        "fact": fact.fact if fact else "",
        "fact_detail": fact.detail if fact else "",
        "analyzer_name": fact.provenance.analyzer if fact and fact.provenance else "",
        "analyzer_version": fact.provenance.version if fact and fact.provenance else "",
    }


class RefractError(Exception):
    """Raised when the Refract CLI returns a non-zero exit code."""
    pass


class Refract:
    """Python SDK for Refract.

    Wraps the `refract` CLI via subprocess. Requires the Refract CLI to be
    installed (``npm install -g @refract-org/cli``).

    Args:
        binary: Path to the ``refract`` binary. If None, searches PATH for
            ``refract`` then falls back to ``npx @refract-org/cli``.
    """

    def __init__(self, binary: str | None = None):
        self._binary = self._find_binary(binary)

    @staticmethod
    def _find_binary(preferred: str | None) -> str:
        if preferred and shutil.which(preferred):
            return preferred
        if shutil.which("refract"):
            return "refract"
        if shutil.which("npx"):
            return "npx"
        if shutil.which("node"):
            return "npx"
        raise RefractError(
            "The Refract CLI is required but not found.\n"
            "Install it: npm install -g @refract-org/cli\n"
            "Or ensure Node.js is installed: https://nodejs.org"
        )

    def _run(self, args: list[str]) -> str:
        cmd = [self._binary, *args]
        if self._binary == "npx":
            cmd = ["npx", "@refract-org/cli", *args]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        except FileNotFoundError:
            raise RefractError(
                "The Refract CLI is required but not found.\n"
                "Install it: npm install -g @refract-org/cli\n"
                "Or ensure Node.js is installed: https://nodejs.org\n"
                "Docs: https://refract-org.github.io/refract-docs/install/"
            )
        if result.returncode != 0:
            raise RefractError(
                f"refract CLI exited with code {result.returncode}: {result.stderr.strip()}"
            )
        return result.stdout

    def analyze(
        self, page: str, depth: str = "brief", as_frame: bool = False, **kwargs: str
    ) -> list[EvidenceEvent] | Any:
        """Analyze a Wikipedia page.

        Args:
            page: Page title.
            depth: Analysis depth (brief, detailed, forensic).
            as_frame: If True, return a pandas DataFrame (requires pandas).
            **kwargs: Additional CLI flags (api, since, etc.).

        Returns:
            List of EvidenceEvent objects, or a DataFrame if as_frame=True.
        """
        args = ["analyze", page, "--depth", depth, "--json"]
        for k, v in kwargs.items():
            args.extend([f"--{k.replace('_', '-')}", v])
        stdout = self._run(args)
        # Parse NDJSON output
        events = []
        for line in stdout.strip().split("\n"):
            if line:
                events.append(_parse_event(json.loads(line)))
        if as_frame:
            import pandas as pd  # type: ignore
            return pd.DataFrame([_flatten_event(e) for e in events])
        return events

    def export(
        self,
        page: str,
        format: str = "ndjson",
        flatten: bool = False,
        as_frame: bool = False,
        **kwargs: str,
    ) -> list[EvidenceEvent] | Any:
        """Export analysis results.

        Args:
            page: Page title.
            format: Output format (json, csv, ndjson).
            flatten: Flatten nested fields (for CSV).
            as_frame: If True, return a pandas DataFrame.
            **kwargs: Additional CLI flags.

        Returns:
            List of EvidenceEvent objects, or a DataFrame if as_frame=True.
        """
        args = ["export", page, "--format", format]
        if flatten:
            args.append("--flatten")
        for k, v in kwargs.items():
            args.extend([f"--{k.replace('_', '-')}", v])
        stdout = self._run(args)
        if format == "ndjson":
            events = []
            for line in stdout.strip().split("\n"):
                if line:
                    events.append(_parse_event(json.loads(line)))
            if as_frame:
                import pandas as pd
                return pd.DataFrame([_flatten_event(e) for e in events])
            return events
        return stdout
