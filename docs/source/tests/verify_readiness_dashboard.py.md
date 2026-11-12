# Readiness dashboard regression evidence

**What:** solver-free tests of source-model identity, evidence SHA, required review keys, file availability and fail-closed status. **When:** any readiness assessment, model-binding or draft check change. **Why:** an incomplete checklist or another project's model must never be promoted as current-project approval.

**How:** temporary project folders, SHA-256 model files, synthetic draft JSON and mocked repeat-file hashing; assert that subset-only review and external project model remain `DIAGNOSTIC_ONLY`. Tests never run OpenSees, ETABS or approve materials.

**Where:** source `tests/verify_readiness_dashboard.py`; implementation `components/model/readiness_dashboard.py`. **Which:** synthetic model/draft files, never sensitive exports. **Who:** software reviewer checks CI; structural research adviser independently reviews model-specific evidence.

**Run:** `python -m unittest tests.verify_readiness_dashboard -v`. **Limitation:** even a complete recorded checklist is only `MODEL_BOUND_SIGNOFF_RECORDED_NOT_AUTOMATICALLY_VERIFIED`; full nonlinear readiness needs separate physical and numerical acceptance.
