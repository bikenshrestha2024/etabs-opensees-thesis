# ETABS audit CLI tests

**Source:** `tests/test_etabs_audit_cli.py`.

Writes small real `.xlsx` files in the ETABS table layout and runs the actual `tools/audit_beam_force_shards.py` code: complete shards (an element cut at the first shard and recovered by the next) pass with exit 0 and a path-free report; an unrecovered cut exits 1; an existing output file is never overwritten; the source workbook bytes are unchanged; a wrong sheet name fails loudly. For `tools/audit_etabs_lot_consistency.py` it checks that report identity keeps file name and SHA but drops local paths, and that an existing report is not overwritten. The full six-lot run is covered by the pinned evidence tests, not here.
