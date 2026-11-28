# ETABS beam-force shard tests

**Source:** `tests/test_etabs_beam_force_shards.py`.

Logic tests use hand-built shards (cut element recovered by the next shard, unrecovered cut, conflicting repeat, duplicate inside a shard, missing force value, frame-table mismatch, text/float key agreement). `PinnedRealBeamEvidenceTests` reads the audit produced from the three real beam workbooks and fails if its measured invariants drift. Passing is not native ETABS/OpenSees acceptance.
