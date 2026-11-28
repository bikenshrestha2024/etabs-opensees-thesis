# ETABS beam-force shard audit (2026-11-28)

**Status: `REFERENCE_ONLY_NOT_ENGINEERING_ACCEPTANCE`.** Evidence: [`20261128_ETABS_BEAM_FORCE_SHARDS_AUDIT.json`](20261128_ETABS_BEAM_FORCE_SHARDS_AUDIT.json) (hashes and aggregates only), produced by `tools/audit_beam_force_shards.py` from the real `Beam_Forces_Element_1/2/3_latest.xlsx` (read-only, every row streamed). This closes the "beam workbooks not supplied" gap recorded in [20261128_ETABS_LOT_CONSISTENCY_AUDIT.md](20261128_ETABS_LOT_CONSISTENCY_AUDIT.md); it does not make any OpenSees comparison.

## Result

The three workbooks are shards of one `Element Forces - Beams` table. Each has one data sheet plus `Program Control`.

| Shard | Data rows | Elements | Note |
|---|---|---|---|
| beam_1 | 1,048,573 | 330 | ends exactly at Excel's 1,048,576-row limit (3 header rows) |
| beam_2 | 1,048,573 | 330 | ends exactly at the Excel row limit |
| beam_3 | 477,700 | 150 | ends below the limit, so the export is not cut after this shard |

* **Union:** 750 elements (30 beams on each of Story1–Story25), 146 cases, 281 case/step keys, 2,388,500 unique rows. Every element has every case/step at every station (500 beams with 11 stations, 250 with 12): no element is incomplete, so the cuts at the Excel limit were recovered by the next shard.
* **Overlap:** 30 elements are cut at each boundary and repeated whole in the next shard (beam_1&2 and beam_2&3). 186,346 rows (2 × 93,173) are exported twice with bit-identical P, V2, V3, T, M2, M3. Keep one copy of each key; do not append the shards.
* **No** repeated key inside a shard, **no** missing or nonfinite force value.
* **Frame table:** all 750 beam elements exist in `Objects and Elements - Frames` (second lot) on the same story.
* Case types in the union: Combination (max/min), LinStatic (step by step), NonModHist (max/min only), LinModRitz, LinRespSpec, NonStatic. Beam time-history rows are Max/Min envelopes, the same limitation as the analysis lots: no beam force history.

## Not established

Beam forces versus OpenSees, beam rigid-end offsets (first station is 0.55 m, not 0), design acceptance and NLTHA. Beam envelopes must not be added across cases.
