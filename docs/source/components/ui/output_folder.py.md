# output_folder.py — implementation guide

**Source:** [components/ui/output_folder.py](../../../../components/ui/output_folder.py)
**Workstream:** All analysis windows. Added on branch `improve/damping-energy-viz` (2026-11-07).

## What it does

A shared "Open output folder" action: `add_open_output_button`, `open_folder` (Windows `os.startfile`, otherwise `xdg-open`/`open`), and `offer_open_folder` (a completion dialog that asks whether to open the results). A missing folder is reported, never created. It is used by the modal, linear and nonlinear time-history, MRSM, irregularity-review and literature-demo windows.

## References

Repository run-order convention (one isolated output folder per analysis). Tag convention: [REF_TAG_CONVENTION.md](../../../../docs/REF_TAG_CONVENTION.md).

## Verification

Test: `tests/verify_aw_sources_and_thickness.py`. Fake-ETABS and synthetic-file tests only; a live ETABS session is not exercised.

[Guide index](../../00_SOURCE_GUIDE_INDEX.md) · [Thesis gates](../../../../docs/00_THESIS_ACCEPTANCE_GATES.md)
