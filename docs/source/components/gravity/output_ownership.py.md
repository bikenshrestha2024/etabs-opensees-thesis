# Gravity output ownership — source documentation

**Source:** `components/gravity/output_ownership.py`  
**Status:** Implementation-level output-routing contract; does not certify native ETABS/OpenSees agreement.

## Purpose

Every *new* gravity file belongs to the selected model's single `02_GRAVITY/RUNS/<model-name>` workspace. Within it:

- `00_INDEXES/`: SHA-verified case registry, latest upload pointer, and small evidence pointers. **No duplicated plots**.
- `01_LOGS/`: GUI action log. Actual solver logs remain with individual solved cases.
- `02_RESULTS/<strategy>/<load-profile>/<timestamp>/`: one immutable full solver run per support strategy, with its JSON, Python runner, logs, Excel and plots. Individual runs are not overwritten.
- `03_EXCEL/`, `04_FIGURES/`: reserved for future stage-level summary exports; do not duplicate existing case artifacts to populate them.
- `05_COMPARISONS/`: timestamped 32/76/97 comparison and two-condition sensitivity runs.
- `06_REVIEW/`: source restraint and native-equivalence preflight reports.
- `07_EXPORT_ZIP/Gravity_Evidence_Upload/`: independently versioned evidence packages; package content necessarily copies files into a ZIP, but the registry no longer copies preview plots.

## Physical source and acceptance

`SCENARIOS` are **different boundary-condition models**, not copies of a single result:

1. `ETABS_NONZERO_REACTION_DIAGNOSTIC` = mapped 32-point diagnostic with 44 source support restraints released; this is **not automatically** native ETABS equivalence.
2. `ETABS_SOURCE_SUPPORTS` = original 76 source-restraint configuration.
3. `CONTINUOUS_WALL_BASE_FIXED` = 97-node fixed wall-base sensitivity.

The registry binds source model hash, input fingerprints, support-set identity, gravity load profile, and exact response SHA256. The output library must not combine or select cases based on matching load totals alone.

## Migration policy

Old `OpenSees_Analysis_Results`, `02_GRAVITY/<support strategy>`, legacy root indexes and `REVIEW_SNAPSHOTS` are **read-only compatibility evidence**. Do not automatically remove, move, hard-link or repackage them as fresh runs. New organized case indexes store one JSON pointer to the source response and do **not** create duplicate PNG folders. Native Windows test must verify GUI output location, historical reads, 32/76/97 case selection and source SHA consistency before merging.

Use `tests/test_gravity_single_owner_layout.py` and the existing gravity evidence/registry tests. The output routing controls no numerical model properties and implies no NBC 105 certification.
