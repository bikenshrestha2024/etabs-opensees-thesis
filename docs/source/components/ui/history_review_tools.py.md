# history_review_tools.py

**Role:** Local Tk time-history accessibility and review evidence export shared by Linear and Nonlinear time history GUIs. No calls to ETABS, OpenSees, remote APIs, or shell execution.

**Inputs:** Parent Tk frame and its Text widget for scrollbar attachment; an existing output directory path; analysis identifier `linear` or `nonlinear`; optional per-file byte limit.

**Outputs:** In-process Tk scrollbar widgets; user-confirmed `Review_ZIPs/<analysis>_<timestamp>.zip` with relative-file SHA256 inventory (`REVIEW_EVIDENCE_MANIFEST.json`).

**Side effects:** Adds only a new local ZIP in the selected output folder; never overwrites original results or source models. Hidden files, symlinks, existing archives, EDB/credential extensions and over-limit files are excluded. May contain unredacted personal paths inside logs; user must review before sharing.

**Units:** SHA256 is dimensionless; byte limits in bytes; physical values are copied unchanged. The module does not derive structural results or change kN-m-s quantities.

**Verification:** `python -m unittest discover -s tests -p test_history_review_tools.py -v`; the workflow also checks syntax. Windows Tk manual scrolling and OpenSees executable tests are separate requirements.

**Engineering scope:** This is packaging and UI functionality only, not NBC 105:2025 code acceptance, model calibration or full-record qualification. See `docs/review/20261111_HISTORY_GUI_SECURITY_AND_PHYSICS.md`.
