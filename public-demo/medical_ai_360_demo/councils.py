"""Names and intentionally minimal behavior of eight simulated councils."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Council:
    key: str
    name: str
    focus: str
    topic_words: tuple[str, ...]

    def receive(self, evidence: tuple[dict[str, str], ...]) -> dict[str, object]:
        """Produce a routing acknowledgment, NOT a medical analysis."""
        matches = tuple(
            item["id"]
            for item in evidence
            if any(word in item["statement"].casefold() for word in self.topic_words)
        )
        return {
            "council": self.key,
            "status": "SIMULATED_RECEIPT",
            "evidence_ids": [item["id"] for item in evidence],
            "topic_matches": list(matches),
            "note": "Routing demonstration only; no clinical interpretation was performed.",
        }


COUNCILS: tuple[Council, ...] = (
    Council("coordinator", "Medical Intelligence Coordinator", "Workflow routing and audit", ("update",)),
    Council("oncology", "Dual Oncology Reviews", "Two separate simulated research perspectives", ("cancer", "oncology", "treatment")),
    Council("nutrition", "Nutrition", "Appetite, hydration and nutrition notes", ("appetite", "food", "hydration")),
    Council("rehabilitation", "Exercise & Rehabilitation", "Movement and daily functioning notes", ("walk", "mobility", "exercise")),
    Council("sleep", "Sleep & Recovery", "Sleep, fatigue and breathing-related notes", ("sleep", "fatigue", "breathing")),
    Council("organ_health", "Organ Health", "Organ-related observations", ("breathing", "blood", "kidney", "liver")),
    Council("medication", "Medication Intelligence", "Medication mentions, without interaction checks", ("medicine", "medication", "treatment")),
    Council("quality_of_life", "Quality of Life", "Comfort, independence and caregiver notes", ("comfort", "tired", "fatigue", "caregiver")),
)

COUNCIL_MAP = {c.key: c for c in COUNCILS}
