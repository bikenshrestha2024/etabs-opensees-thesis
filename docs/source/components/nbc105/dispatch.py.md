# NBC 105 dispatch.py — ten-clause production interface

**Source:** [components/nbc105/dispatch.py](../../../../components/nbc105/dispatch.py)

**Owner:** Invocation and serialization only. It does **not** own any equation or engineering factor. The matching `clause_NN_*.py` remains the sole numerical source. [Clause register](../../../nbc105/README.md).

**Stable API:** `available_operations()` lists the publicly exported functions declared in each module's `__all__` and physically defined in that module. `run_operation(clause, operation, inputs)` invokes only those functions with named JSON-compatible parameters; it rejects unsupported function names, unregistered clauses, malformed input and nonfinite outputs.

**Engineering limitation:** Every result reports `CODE_CALCULATION_ONLY_NOT_BUILDING_ACCEPTANCE`. Successful computation is not certification of ETABS restraints, gravity, periods, drift, components, nonlinear wall convergence or matched model provenance.

**Tests:** `tests/test_nbc105_module_dispatch.py`, plus original clause regression suites. Private EDBs and model data never leave the user's Windows computer through the dispatcher.

**Public action:** `python -m components.nbc105 --list` and `python -m components.nbc105 --clause 10 --operation component_amplification_factor --json '{"building_period_s":1,"component_period_s":1.25}'`.
