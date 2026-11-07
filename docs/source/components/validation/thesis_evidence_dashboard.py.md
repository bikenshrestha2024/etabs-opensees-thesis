# Thesis evidence dashboard — source guide

Source: [thesis_evidence_dashboard.py](../../../../components/validation/thesis_evidence_dashboard.py)

This is a **read-only provenance and stage-dependency screen**, NOT a substitute for the repository's existing physics gates, native OpenSees runs or NBC 105:2025 design checks. It reads a reviewer-authored JSON manifest, hashes each locally referenced evidence file and emits a status CSV for Excel, audit JSON and optional Matplotlib PNG. It never edits ETABS, OpenSees, ground motions or result files.

The stages follow [canonical run order](../../../review/00_CANONICAL_RUN_ORDER_AND_NAMING.md) and the [P0 issue ledger](../../../review/00_ACTIVE_CODE_ENGINEERING_REVIEW.md). A claimed VERIFIED stage is blocked if files are missing, SHA256 differs or a preceding stage is unverified. Source identity can never prove physical correctness; `engineering_accepted` is always false.

Run tests: [verify_thesis_evidence_dashboard.py](../../../../tests/verify_thesis_evidence_dashboard.py).
