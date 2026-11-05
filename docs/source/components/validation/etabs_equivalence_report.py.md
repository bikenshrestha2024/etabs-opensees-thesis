# etabs_equivalence_report.py.md — per-module engineering source guide

**Source:** [etabs_equivalence_report.py](../../../../components/validation/etabs_equivalence_report.py)

Evidence-gated exact semantic-key comparator. Exposes configurable research screening tolerances, zero-reference absolute thresholds, explicit PASS/FAIL/NOT_COMPARABLE/MISSING_ETABS/MISSING_OPENSEES states. Generates Excel with result records, case/status summary and profile charts; source file read-only. No automated NBC code certification. Uses openpyxl; tests/verify_etabs_direct_equivalence.py.

**Contract and engineering restrictions:** See [full ETABS API equivalence guide](../../../validation/etabs_direct/README.md). ETABS spectrum methods, envelopes, damping, eigenmode pairing, point coordinates, seismic mass, CQC and NBC §§7.3–7.5 must be independently reconciled. Numeric tolerance is not a structural design PASS.

**Verification:** GitHub Linux mock API regression; native Windows ETABS v23 integration and actual ETABS/OpenSees numerical validation remain NOT RUN. Keep source files private/local and preserve original SHA256 evidence.
