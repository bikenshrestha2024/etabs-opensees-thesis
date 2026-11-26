# components/nbc105/normative_register.py

**Source:** `components/nbc105/normative_register.py`

**Authority:** the sentence-level register `docs/nbc105/normative_register/NORMATIVE_REGISTER.csv` built from the user's NBC 105:2025 PDF (see [the register guide](../../../nbc105/NORMATIVE_REGISTER_GUIDE.md)). No standard text is stored; each row has a locator, a SHA-256 of the normalised unit and one disposition.

**Purpose:** load the register, validate its structure and references (ast based, nothing is imported or executed), count rows per clause and disposition, and run a fail-closed gate.

**Public API:** `load_register()`, `validate_register(rows)`, `summarize_register(rows)`, `normative_register_gate(rows=None)`, constants `DISPOSITIONS`, `REGISTER_COLUMNS`, `EXTERNAL_GATES`.

**Gate.** `BLOCKED_NOT_CERTIFIED` when a row is unreviewed or `UNVERIFIED_GAP`, a row is invalid, a reference does not resolve, the register is unreadable or its row count differs from the manifest. `REGISTER_REVIEWED_EXTERNAL_GATES_OPEN` when every row has a valid disposition. `certified` is always `False`; there is no certified status.

**Units:** none. **Invocation:** `python -m components.nbc105 --audit` (adds the key `normative_register`, exit code 2) and `components.nbc105.acceptance.evaluate_project_evidence` (adds metrics to the `full_nbc_source_requirement_audit` gate, which stays OPEN).

**Tests:** `tests/test_nbc105_normative_register.py`, `tests/test_nbc105_normative_evidence.py`.
