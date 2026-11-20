# Headless pytest configuration and CI job (follow-up Task 3)

Editor Claude Code (model label UNKNOWN). Base SHA `951ee77`, branch `feat/readiness-binding-ci-audit`. Plan: `docs/superpowers/plans/2026-11-20-binding-ci-audit.md` Task 3.

Edited paths
- `pytest.ini` (new), `requirements-ci.txt` (new), `conftest.py` (new), `.github/workflows/tests.yml` (new), `docs/00_REPOSITORY_ORGANIZATION.md` (section appended).
- No V### shim, test assertion, existing workflow or Saved_Project_V156 file was changed.

Tests actually run (Linux sandbox, Python 3.13, no tkinter/plotly/comtypes)
- Before: `PYTHONPATH=$PWD python -m pytest -q -p no:cacheprovider --continue-on-collection-errors tests` -> 8 failed, 539 passed, 4 collection errors. Same command on `tests/verify_*.py` -> 9 failed, 647 passed, 2 skipped, 13 collection errors (shapely installed).
- After: `python -m pytest -q` -> 2 failed, 1186 passed, 34 skipped, 0 errors; also reproduced in a clean venv from `requirements-ci.txt`.
- Probe: an assertion failure, an unrelated ModuleNotFoundError and an unrelated ImportError still fail; `import tkinter` skips (fails with THESIS_STRICT_OPTIONAL_IMPORTS=1). Probe file removed.
- Remaining failures, not masked: `tests/verify_ref_tags.py` (public symbols added in Tasks 1-2 lack [REF] tags) and `tests/verify_review_ledger.py` (needs full git history; sandbox clone is shallow).

PENDING: GitHub-hosted run of `.github/workflows/tests.yml` (not run); Python 3.12 (sandbox used 3.13); native Windows/ETABS and tkinter/plotly tests (skipped here, not passed).
