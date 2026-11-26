# NBC 105:2025 normative-unit register

Editor Claude Code (model label UNKNOWN). Branch `feat/nbc105-normative-sentence-audit`, base `250c695`.

Stage 1: `tools/nbc105_normative_extract.py`, `tests/test_nbc105_normative_extract.py`, `docs/source/tools/nbc105_normative_extract.py.md`, `docs/nbc105/normative_register/` (register CSV, manifest), one `engineering/registry/CANONICAL_MODULES.csv` row.

Stage 2: `docs/nbc105/normative_register/DISPOSITION_RULES.csv` (486 rules), full dispositions for all 1417 rows, `tests/test_nbc105_normative_evidence.py` (pins of printed values and boundaries; no production code changed, no transcription bug found).

Stage 3: `components/nbc105/normative_register.py` (+ guide, registry row, `tests/test_nbc105_normative_register.py`), `compliance_coverage.full_audit`, `--audit` and `acceptance.py` wiring (adds register metrics, gates stay OPEN), `docs/nbc105/NORMATIVE_REGISTER_GUIDE.md`, README and exhaustive-register updates, `CLAUSE_SUMMARY.md`.

Tests: unit tests only. No native ETABS/OpenSees. Source EDB untouched. The standard is not certified; dispositions are source-to-code review notes, not engineering acceptance.
