# tools/audit_knowledge_map.py — source guide

**What:** offline 5W1H knowledge register checker for `KNOWLEDGE_BASE/01_WORKFLOWS/WORKFLOW_CARDS.csv`.

**When:** after adding a workflow, changing its canonical source or guide, and before merge.

**Why:** keep documentation pointers discoverable and preserve canonical modules, avoiding untested import/file relocations.

**How:** Python 3.12 standard-library CSV parser verifies every required field, unique IDs, repo-relative safe paths, and source/guide existence; exits 1 when invalid. `python tools/audit_knowledge_map.py` is read-only unless `--json-out path` is explicitly supplied. No network, solver import or project data scan.

**Where:** source `tools/audit_knowledge_map.py`, output stdout or optional local JSON; tests `tests/test_knowledge_map.py`.

**Which:** exact source paths, guides and owner roles from workflow CSV, not arbitrary external paths.

**Who:** software maintainer maintains code/schema; researcher updates workflow descriptions; structural engineer verifies physical statements.

**Limitations:** a valid index does not mean source-code semantic audit, numerical convergence, material calibration, ETABS equivalence or NBC acceptance. Current root-relative paths remain immutable for backwards compatibility.

**Reference:** [knowledge base](../../../KNOWLEDGE_BASE/README.md) and [repository governance](../../../engineering/rules/CORE_RULES.md).
