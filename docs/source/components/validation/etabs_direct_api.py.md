# etabs_direct_api.py.md — per-module engineering source guide

**Source:** [etabs_direct_api.py](../../../../components/validation/etabs_direct_api.py)

Reads exact source-matched ETABS API modal period/mass, spectrum base reaction, story drift and mapped joint displacement. Input explicit reviewed case/story/point mapping and active EDB; output normalized kN-m-s result rows. Calls temporary Results.Setup and SetPresentUnits(6) and restores them in finally. Refuses mismatched EDB and unavailable/incorrect COM results. Never runs, saves, unlocks, edits, or uploads EDB. Official CSI ETABS API 2016 signature reference, native ETABS v23 binding NOT YET TESTED. New tests: tests/verify_etabs_direct_equivalence.py.

**Contract and engineering restrictions:** See [full ETABS API equivalence guide](../../../validation/etabs_direct/README.md). ETABS spectrum methods, envelopes, damping, eigenmode pairing, point coordinates, seismic mass, CQC and NBC §§7.3–7.5 must be independently reconciled. Numeric tolerance is not a structural design PASS.

**Verification:** GitHub Linux mock API regression; native Windows ETABS v23 integration and actual ETABS/OpenSees numerical validation remain NOT RUN. Keep source files private/local and preserve original SHA256 evidence.

## 2026-11-22: real case/combination inventory without fabricated equivalence

`discover_native_base_reactions(sap, source_edb, max_cases=250)` checks that the already-open ETABS model filename exactly equals the requested local original EDB, fingerprints its bytes, snapshots original CSI Results.Setup case/combination selections and present units, switches to kN-m-C, enumerates *actual native* case/combination names, and reads returned `BaseReact()` components. Source setup and units are restored in `finally`, including partial failures. Missing/unanalysed cases are listed in `excluded`, not replaced with zero. Raw signed reactions are independent of exact source reviewed MRSM CQC scale/response basis. The mock CSI interface is covered in `tests/test_native_etabs_and_ltha_preflight_20261122.py`; the native Windows ETABS 23 API and original analyzed EDB are **NOT TESTED** in the CI environment.
