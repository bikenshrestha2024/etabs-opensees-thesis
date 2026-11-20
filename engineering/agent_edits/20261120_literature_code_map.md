# Literature-to-code map and damped-outrigger gap register (follow-up Task 4)

Editor Claude Code (model label UNKNOWN). Base SHA `2348cfb`, branch `feat/readiness-binding-ci-audit`. Plan: `docs/superpowers/plans/2026-11-20-binding-ci-audit.md` Task 4.

Existing-code search: `LITERATURE/tools/audit_source_citations.py` indexes DOI/URL strings from git-tracked files into `LITERATURE/` only (no R-ID, `[REF]` tag or tests split, no UNIMPLEMENTED status), and `tools/audit_knowledge_map.py` / `tools/audit_documentation_coverage.py` check guide links, not citations. A new tool was therefore added, registered NEW_WITH_JUSTIFICATION.

Edited paths
- New: `tools/audit_literature_code_map.py`, `tests/test_literature_code_map.py`, `docs/validation/LITERATURE_CODE_MAP.md`, `docs/validation/LITERATURE_CODE_MAP.csv` (generated), `docs/validation/DAMPED_OUTRIGGER_NLTHA_GAP_REGISTER.md` (hand-reviewed), `docs/source/tools/audit_literature_code_map.py.md`, `docs/source/tests/test_literature_code_map.py.md`.
- Modified: `engineering/registry/CANONICAL_MODULES.csv` (one row), `docs/00_REPOSITORY_ORGANIZATION.md` (section appended).
- No component, solver, V### shim, existing test or Saved_Project_V156 file was changed. No PDF was opened; the tool reads only the research register, the master index CSV and `*.py` files.

Tests actually run (Linux sandbox, Python 3.13; `openseespy` does not import here)
- `python -m pytest -q -p no:cacheprovider tests/test_literature_code_map.py` -> 6 passed.
- `python -m pytest -q -p no:cacheprovider tests/verify_ref_tags.py tests/test_documentation_coverage.py tests/verify_documentation_coverage.py` -> 10 passed, 5 subtests passed.
- `python -m pytest -q -p no:cacheprovider tests/test_knowledge_map.py` -> 4 passed; `python tools/audit_knowledge_map.py` -> reported no errors.
- `python -m pytest -p no:cacheprovider -q` (whole suite) -> 1194 passed, 34 skipped, 0 failed.
- Determinism: two consecutive `python tools/audit_literature_code_map.py` runs gave identical SHA-256 for the `.md` and `.csv`; `--check` -> UP_TO_DATE.

Scientific scope
- The gap register was written by reading the cited code. No native OpenSees, ETABS or numerical run supports it. It assigns no component the `PROJECT_VERIFIED` tier. The generated map records citations only (provenance), not validation.
- Finding recorded in the register: R03, R06, R08, R09 and R11 are cited nowhere in components/, src/ or tests/ (re-verified by grep for DOI, URL and author names). Correction: R04 was first listed here as uncited; `components/validation/wall_validation.py` cites it by PEER 2024/11 URL and author names, which the first version of the tool (ID and DOI only) could not see. The tool now also matches Source URL and author-year.

PENDING
- Native OpenSeesPy and ETABS behaviour statements quoted from docstrings (for example the region-damping facts in `damping_regions.py`) are not re-verified.
- NBC 105:2025 clause wording used by the code is not compared with the official PDF.
- Python 3.12 and Windows/Spyder execution of the new tool and test; GitHub-hosted CI run.
- Master-index rows without a DOI (L006, L009, L012, L014) are linked to R01, R04, R07, R11 only on an exact title, year and first-author match and share those citations (`link_basis` column); every other master row without a match shows `UNKNOWN`. Citations that give none of ID, DOI, Source URL with a path or the register author names are not detected.
