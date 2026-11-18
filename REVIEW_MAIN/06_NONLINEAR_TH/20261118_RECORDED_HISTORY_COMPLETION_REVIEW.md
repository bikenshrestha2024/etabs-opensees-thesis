# Soil C completion audit and recorded history

Base commit `fcb3bcc754d1811c3e01f20faec9985f01cde329`. The review covers two functions in `tools/audit_soil_c_case_completion.py`, Git blob `bc60e90b990efb70be7036a0cb2e02a9516c718c`.

| Inspected source | Contract and evidence |
| --- | --- |
| `inspect_case`, lines 38–128 | Reads one orientation's summary, duration gate and CSV. Solver failure reports take precedence. Missing or inconsistent artifacts leave the case incomplete. Examined the CSV writer and duration gate calls in `building_exploratory.py` and the shared validator in `full_record_gate.py`. Time is expressed in seconds. |
| `audit_matrix`, lines 131–171 | Requires exactly 112 unique variant, limit-state and event groups. Calls `inspect_case` for XY and YX and aggregates 224 statuses. An empty set of outputs returns 224 `NOT_RUN` statuses. The return contract leaves model suitability and optimum selection undecided. |

The regression first reproduced a counted completion with two JSON files and no history. The corrected case audit requires `Building_Nonlinear_history.csv` and runs the shared accepted-history validator over its rows. Missing, truncated, nonfinite or malformed traces and sample-count mismatches return `INCOMPLETE`. The case summary and gate still provide the claimed duration and source digests. Independent verification of actual motion and model bytes and physical acceptance remains open.

Local Windows Python 3.12 regression passed for `tests.verify_soil_c_case_completion`, `tests.verify_full_record_gate`, `tests.verify_variant_comparison` and `tests.verify_soil_c_run_matrix` (41 tests). The same Windows pass exposed a CRLF-dependent test fixture in `test_history_run_output_contract.py`. Writing the expected bytes directly preserves its source-immutability assertion.
