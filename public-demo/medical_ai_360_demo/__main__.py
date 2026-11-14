"""Run with: python -m medical_ai_360_demo [--json] [--scenario path]."""

import argparse
from pathlib import Path

from .coordinator import Coordinator, load_fictional_scenario


def main() -> None:
    parser = argparse.ArgumentParser(description="Nonclinical Medical AI Council 360° workflow demonstration")
    parser.add_argument("--json", action="store_true", help="Print inspectable JSON output")
    parser.add_argument("--scenario", type=Path, default=Path(__file__).resolve().parent.parent / "example_data" / "fictional_case.json",
                        help="Path to a LOCAL, explicitly fictional JSON scenario")
    args = parser.parse_args()
    scenario = load_fictional_scenario(args.scenario)
    result = Coordinator().run(scenario)
    if args.json:
        print(result.as_json())
        return
    print("MEDICAL AI COUNCIL 360° — PUBLIC WORKFLOW DEMO")
    print(result.disclaimer)
    print(f"Scenario: {result.scenario_id}")
    print(f"Evidence records: {len(result.evidence)}")
    print(f"Council receipts: {len(result.council_receipts)} / 8")
    print(f"Separate rule-only oncology reviews: {len(result.reviews)}")
    print(f"Simulated phrase alerts: {len(result.alerts)}")
    print("Audit examples:")
    for item in result.events:
        if item.action in {"simulated_safety_alert", "reviews_unsealed_for_comparison", "example_evidence_shared"}:
            print(f"  {item.step:02d} {item.action}: {item.sender} → {item.recipient} ({', '.join(item.evidence_ids)})")
    print("No real medical processing or alerts were performed.")


if __name__ == "__main__":
    main()
