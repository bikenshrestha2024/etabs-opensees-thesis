# ETABS lot consistency tests

**Source:** `tests/test_etabs_lot_consistency.py`.

Logic tests use tiny hand-built tables (support-tag ordering and failure modes, g identification, envelope-only history, event pairing, modal flags, table identity, combined-lot overlap, six-component equilibrium including the moment-transfer sign). `PinnedRealExportEvidenceTests` reads the committed audit produced from the real six-lot export and fails if its measured invariants drift (32 + 44 split, mass source, 55 additive equilibrium rows, envelope-only history, extra events, combined-lot duplicate, zero RZ participation, no local paths). Passing them is not native ETABS/OpenSees acceptance.
