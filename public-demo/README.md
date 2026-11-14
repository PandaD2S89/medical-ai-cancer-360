# Medical AI Council 360° — F*CK Cancer

**Public workflow demo | Python standard library | Simulation only**

Medical AI Council 360° explores how distinct specialist software councils might exchange evidence, preserve independent perspectives, and log safety-related workflow events. Our wider mission is to help families facing cancer have a better fighting chance through better access to understandable, evidence-oriented research support.

> **Not a medical device or clinical tool.** This demo has **no real AI model, no clinical validation, no real alerts, no drug-interaction checking, no live research, and no treatment recommendations**. All patient information is invented. Never enter actual patient data. It does not represent the private implementation.

## Quick start

Requires **Python 3.10+**. No installation or external packages.

From this `public-demo` directory:

```bash
python -m medical_ai_360_demo
python -m medical_ai_360_demo --json
python -m unittest discover -s tests -v
```

The CLI prints an audit-style trace showing a *simulated* safety phrase match, two separately submitted rule-only reviews, all eight council acknowledgments, and selective sharing. The `--json` version prints structured records for examination.

## The eight islands shown

| Island | Demonstrated role |
|---|---|
| 1. Medical Intelligence Coordinator | Registry receipt for workflow/audit; the outer Coordinator orchestrates the example |
| 2. Dual Oncology Reviews | Two separate **rule-only**, nonclinical example reviews A/B |
| 3. Nutrition | Simulated evidence-topic receipt |
| 4. Exercise & Rehabilitation | Simulated evidence-topic receipt |
| 5. Sleep & Recovery | Simulated evidence-topic receipt |
| 6. Organ Health | Simulated evidence-topic receipt |
| 7. Medication Intelligence | Simulated receipt, **no medication safety or discovery logic** |
| 8. Quality of Life | Simulated receipt |

All eight receive the same fictional case. The outer Coordinator records evidence, runs an intentionally simplistic phrase-marker simulation **before** routing, collects two separate reviews before comparing them, and records limited example sharing (nutrition→rehabilitation; sleep→organ health). Message passing is in-process Python calls, not a network bus.

## Fictional scenario

`example_data/fictional_case.json` includes three *invented* notes from a patient and caregiver. One note intentionally contains the exact phrase `worsening breathing` to demonstrate an alert marker. Matching that phrase does **not** establish a real-world emergency; failing to match it does **not** establish safety. No notification is sent.

The output retains each note's `id` and `source` so the demo's evidence references can be audited. The two review functions receive an identical snapshot and do not consume each other's conclusion. Neither uses a language model or medical knowledge base.

## Files

```text
public-demo/
├── README.md
├── TEST_RESULTS.txt
├── .gitignore
├── example_data/fictional_case.json
├── medical_ai_360_demo/
│   ├── __init__.py
│   ├── __main__.py
│   ├── councils.py
│   └── coordinator.py
└── tests/test_demo.py
```

## How to contribute

Useful scoped extensions could include clearer event displays, new **fictional-only** test cases, property-based invariants using standard-library `unittest`, improved source-reference validation, a network-free mock message bus, and failure-injection tests. Please keep any real medical decision-making, patient data, private prompts, secrets, clinical assertions, and third-party code out of contributions.

## Limitations and publication status

This is a **newly written illustrative implementation**, not an extraction or open-source release of the private project. It deliberately does not include the real coordination engine, memory, research discovery, clinician workflows, security infrastructure, LLM settings, or advanced AI reasoning. Passing unit tests measures this example's software behavior, **not medical correctness or clinical reliability**.

**License:** The code in this public demo is available under the repository's [MIT License](../LICENSE). The broader private system is not included. This example is for software collaboration and testing only; it is not medically validated. Do not post real patient information in issues, discussions, or pull requests.
