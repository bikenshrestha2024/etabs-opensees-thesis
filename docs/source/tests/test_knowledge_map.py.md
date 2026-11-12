# tests/test_knowledge_map.py — source guide

**What/when:** deterministic unit tests for the knowledge-map checker, executed in repository integrity CI and before documentation updates.

**Why/how:** create temporary repo-shaped fixtures to assert valid source/guide links, reject missing owners/guides and duplicate IDs, and fail on path traversal. Does not touch the actual ETABS source or native OpenSees.

**Where:** `tests/test_knowledge_map.py`, `tools/audit_knowledge_map.py`.

**Which:** fake CSV/temporary files; no real project input.

**Who:** maintainer owns regression; structural reviewer remains responsible for engineering statements in real cards.

**Run:** `python -m unittest discover -s tests -p 'test_knowledge_map.py' -v`.

**Status:** navigation test only; not engineering validation.
