# Agent change record — 2026-11-15

- **Editor:** ChatGPT (OpenAI GPT-6)
- **Repository baseline:** `248329658b5976c51834e96fe9662b06a955062d`
- **Change category:** EXISTING / small reversible correction to saved gravity comparison consistency
- **Files:** `components/gravity/support_scenarios.py`; `tests/verify_gravity_support_scenarios.py`; review document and attribution record
- **Reviewed reference files:** `AGENTS.md`, `CLAUDE.md`, `engineering/rules/CORE_RULES.md`, `REVIEW_MAIN/README.md`, the active gravity comparison and tests, and integrated audit workflow
- **Preserved:** ETABS EDB and Excel inputs, all physics and model conversion, launcher names, original results, run paths and source material
- **Verification scope:** new mock regression tests; GitHub CI required; native Windows ETABS, OpenSees and Spyder NOT_RUN
- **Claim limitation:** one confirmed output-integrity defect, not complete source-wide semantic inspection or ETABS/OpenSees acceptance
