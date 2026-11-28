# ETABS beam-force shard audit

**Canonical source:** [`components/validation/etabs_beam_force_shards.py`](../../../../components/validation/etabs_beam_force_shards.py)
**Run it with:** [`tools/audit_etabs_beam_force_shards.py`](../../tools/audit_beam_force_shards.py.md) (`tools/audit_beam_force_shards.py`)
**Evidence:** [`docs/validation/20261128_ETABS_BEAM_FORCE_SHARDS_AUDIT.md`](../../../validation/20261128_ETABS_BEAM_FORCE_SHARDS_AUDIT.md)

Excel holds at most 1,048,576 rows, so the `Element Forces - Beams` table arrives as several workbooks. `audit_beam_force_shards(shards, frame_elements=None)` takes ordered `(name, rows)` shards of dict rows and reports:

* per-shard row count and whether the sheet stops at the Excel limit (data rows + 3 header rows);
* the union: unique rows (key = element + case + step type + step number + station), elements, case/step keys, stations per element;
* rows repeated in a later shard and whether their six force values (P, V2, V3, T, M2, M3) agree bit for bit;
* whether every element has every case/step at every station (a cut that no shard recovered is an error);
* optionally, whether each beam element exists on the same story in `Objects and Elements - Frames`.

Only 64-bit key and value hashes are kept in memory, so million-row shards stream. Result is `REFERENCE_ONLY_NOT_ENGINEERING_ACCEPTANCE`: complete shards say nothing about whether the forces match an OpenSees run.
