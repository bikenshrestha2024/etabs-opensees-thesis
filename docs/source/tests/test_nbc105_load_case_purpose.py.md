# Source guide — test_nbc105_load_case_purpose.py

**What:** regression test distinguishing gravity-only 1.0D+1.0L+roof LL from NBC 105 Clause 5.2 seismic load contributions. **When:** after changes to model load factors, classification or gravity comparison reports. **Why:** avoid reporting an intentional load-case difference as a failed equilibrium or treating roof LL as seismic weight.

**How:** pure tests on nominal factors, independent mass factors, explicit storage and unknown category overrides, non-finite/missing inputs and separate source ledger classification. No ETABS, GUI or OpenSees execution.

**Where:** `tests/test_nbc105_load_case_purpose.py`. **Which:** synthetic source names and factor dictionaries; no project files or sensitive data. **Who:** software maintainer reviews tests; structural reviewer confirms the applied code factor table.

**Run:** `python -m unittest discover -s tests -p 'test_nbc105_load_case_purpose.py' -v`.

**Gate:** test success is not an engineering acceptance or full gravity validation.
