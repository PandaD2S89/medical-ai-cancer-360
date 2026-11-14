"""Tiny synchronous Coordinator; explicit simulation, not clinical software.

This code is newly written for public demonstration and uses only Python's
standard library. It does NOT implement the project's private architecture.
"""

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any

from .councils import COUNCILS, COUNCIL_MAP


DISCLAIMER = (
    "SIMULATION ONLY — no medical decisions, clinical triage, treatment advice, "
    "actual alerts, AI inference, or live research. NEVER use real patient data."
)

# This is a deliberately simplistic *synthetic marker*. It is NOT a reliable
# warning detector and may produce both false positives and false negatives.
SYNTHETIC_ALERT_MARKERS = ("worsening breathing", "demo alert marker")


@dataclass(frozen=True)
class Event:
    step: int
    action: str
    sender: str
    recipient: str
    evidence_ids: tuple[str, ...]
    note: str


@dataclass(frozen=True)
class Review:
    reviewer: str
    perspective: str
    evidence_ids: tuple[str, ...]
    result: str
    status: str = "SIMULATED_ONLY"


@dataclass(frozen=True)
class Alert:
    evidence_id: str
    kind: str
    status: str
    note: str


@dataclass
class DemoResult:
    scenario_id: str
    disclaimer: str
    evidence: list[dict[str, str]]
    events: list[Event]
    council_receipts: list[dict[str, object]]
    reviews: list[Review]
    alerts: list[Alert]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def as_json(self) -> str:
        return json.dumps(self.as_dict(), indent=2, ensure_ascii=False)


def validate_fictional_scenario(data: object) -> dict[str, Any]:
    """Reject unmarked or malformed examples; this is NOT a privacy detector."""
    if not isinstance(data, dict) or data.get("fictional") is not True:
        raise ValueError("Only explicitly fictional example scenarios are allowed")
    scenario_id = data.get("scenario_id")
    evidence = data.get("evidence")
    if not isinstance(scenario_id, str) or not scenario_id or len(scenario_id) > 80:
        raise ValueError("scenario_id must be a short nonempty string")
    if not isinstance(evidence, list) or not 1 <= len(evidence) <= 20:
        raise ValueError("evidence must contain 1–20 fictional observations")
    ids: set[str] = set()
    for item in evidence:
        if not isinstance(item, dict):
            raise ValueError("each evidence item must be an object")
        for name, limit in (("id", 40), ("source", 100), ("statement", 500)):
            value = item.get(name)
            if not isinstance(value, str) or not value.strip() or len(value) > limit:
                raise ValueError(f"each evidence item requires a short {name}")
        if item["id"] in ids:
            raise ValueError("duplicate evidence IDs are not allowed")
        ids.add(item["id"])
    return data


def load_fictional_scenario(path: str | Path) -> dict[str, Any]:
    """Load JSON locally; no network, external services, or file writes."""
    with Path(path).open("r", encoding="utf-8") as handle:
        return validate_fictional_scenario(json.load(handle))


def _review_a(evidence: tuple[dict[str, str], ...]) -> Review:
    """Separate, rule-only perspective A; never sees perspective B's output."""
    return Review(
        reviewer="oncology_A",
        perspective="Established-evidence questions (illustration)",
        evidence_ids=tuple(item["id"] for item in evidence),
        result="Flag fictional observations for source verification by human experts; no conclusions made.",
    )


def _review_b(evidence: tuple[dict[str, str], ...]) -> Review:
    """Separate, rule-only perspective B; never sees perspective A's output."""
    return Review(
        reviewer="oncology_B",
        perspective="Uncertainty and missing-evidence questions (illustration)",
        evidence_ids=tuple(item["id"] for item in evidence),
        result="Note that this short fictional account cannot support medical conclusions.",
    )


class Coordinator:
    """Single-process message simulation with an inspectable event sequence."""

    def run(self, scenario: object) -> DemoResult:
        data = validate_fictional_scenario(scenario)
        evidence = tuple(
            {"id": item["id"], "source": item["source"], "statement": item["statement"]}
            for item in data["evidence"]
        )
        events: list[Event] = []

        def record(action: str, sender: str, recipient: str, refs: tuple[str, ...], note: str) -> None:
            events.append(Event(len(events) + 1, action, sender, recipient, refs, note))

        for item in evidence:
            record("evidence_recorded", item["source"], "coordinator", (item["id"],), "Fictional source retained")

        # Put the illustrative synthetic alert check BEFORE any council work.
        alerts: list[Alert] = []
        for item in evidence:
            if any(marker in item["statement"].casefold() for marker in SYNTHETIC_ALERT_MARKERS):
                alerts.append(Alert(
                    item["id"], "SYNTHETIC_PHRASE_MATCH", "SIMULATED_ONLY",
                    "Demonstration event logged; no real alert or clinical triage occurred.",
                ))
                record("simulated_safety_alert", "safety_example", "human_review_placeholder", (item["id"],),
                       "Synthetic marker found; no notification sent")
        record("safety_example_completed", "safety_example", "coordinator", (),
               "Simple phrase matching only; NOT a clinical safety screen")

        # Both reviewers receive the same immutable snapshot and submit before
        # anything is revealed/comparable. They are NOT LLM agents.
        first = _review_a(evidence)
        record("sealed_review_submitted", "oncology_A", "coordinator", first.evidence_ids,
               "Perspective A held from B")
        second = _review_b(evidence)
        record("sealed_review_submitted", "oncology_B", "coordinator", second.evidence_ids,
               "Perspective B held from A")
        reviews = [first, second]
        record("reviews_unsealed_for_comparison", "coordinator", "public_demo_viewer", first.evidence_ids,
               "Both separate simulated reviews are now visible")

        receipts: list[dict[str, object]] = []
        all_refs = tuple(item["id"] for item in evidence)
        for council in COUNCILS:
            record("task_routed", "coordinator", council.key, all_refs,
                   "Fictional case forwarded to simulated council")
            response = council.receive(evidence)
            receipts.append(response)
            record("receipt_returned", council.key, "coordinator", all_refs,
                   "Simulation receipt; not a clinical finding")

        # Two concrete examples of selective inter-council sharing.
        sharing_examples = (
            ("nutrition", "rehabilitation", "appetite"),
            ("sleep", "organ_health", "breathing"),
        )
        for origin, destination, word in sharing_examples:
            matched = tuple(item["id"] for item in evidence if word in item["statement"].casefold())
            if matched:
                assert origin in COUNCIL_MAP and destination in COUNCIL_MAP
                record("example_evidence_shared", origin, destination, matched,
                       "Demo only: source IDs shared, no assessment or action performed")

        return DemoResult(data["scenario_id"], DISCLAIMER, list(evidence), events, receipts, reviews, alerts)
