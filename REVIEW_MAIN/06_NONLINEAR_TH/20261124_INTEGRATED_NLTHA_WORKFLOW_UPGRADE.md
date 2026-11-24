# Integrated exploratory NLTHA workflow upgrade — 2026-11-24

## Scope and invariant decisions

This change extends the current V138 research runner; it is not a second structural solver or an approval pathway. The user's 32 physical foundations and 44 additional shear-wall mesh points remain unchanged. Full gravity benchmark remains 1.0D+1.0L, distinct from NBC 105:2025 Table 5-1 seismic weight. No wall geometry, beam self-weight policy, material constants, reinforcement, damping target, convergence tolerance or source EDB was changed by this integration. Source native EDB/workbook hashes are unavailable in this coding session. Native support transfer and production NLTHA gates remain unresolved.

## Operator procedure

1. Update the repository. Open the main launcher, select the original ETABS export, then use **Select verified clear-beam model** and select the completed canonical rebuild. The shared folder variable routes newly opened stage windows to that folder; close windows launched for the prior model. An export-verified rebuild is not a solved gravity model.
2. Rerun gravity, ESM/Rayleigh, modal, MRSM and time-history checks for the selected model. Do not reuse a reference with another model fingerprint.
3. In the exploratory nonlinear runner, select the source literature basis and records. Initial mode count defaults to 40, cap 80, increments 20; explicit configs may set initial_modes and maximum_initial_modes (hard cap 160). Default exploratory first/20th-mode damping remains unchanged.
4. For one job, inspect Transient_Performance.json, Nonlinear_Initial_Modal_Audit.json, Research_Material_Assignment_V161.json and Material_Model_Binding.json. These separate source identity, numerical progression and unapproved literature transfer.
5. For multiple independent jobs, open **NLTHA independent model / record batch**. Select saved Requested_Config JSON files for the desired source models and orientations. Choose 1–4 workers; default 1. Split XY and YX into distinct configurations if concurrent orientation analysis is intended. Each job is a separate V138 process, no shared OpenSees domain. Output folders are unique. Batch_Status.json records process state and input digests. Stop requests preserve partial results. CLI equivalent: python -m components.nonlinear_time_history.batch_execution --plan PLAN.json --output NEW_DIR --workers 2. PLAN.json contains a jobs array of config paths.

## Verification ledger

- GitHub connector readback and successful commit responses: observed.
- Three isolated Python modal-helper checks (copied source excerpt, simulated eigen solver): passed, covering 40-to-60 stop, 40-to-60-to-65 cap, hard limit validation.
- Repository pytest regression suite: tests/test_integrated_research_nltha_upgrade.py authored; not executed against the complete checkout in this session (container cannot resolve GitHub).
- GitHub combined status query returned no status checks; CI not established.
- Native Windows ETABS/OpenSees, GUI, independent concurrent jobs, support/MPC equivalence, full record response, actual speed-up: NOT_VERIFIED.
- Read-first governance files were consulted during the task rather than before the first source edit; the required preflight ordering and full red-green cycle were not satisfied. The changes need independent review.

## Engineering gates

SOURCE_CHECKED (software interface review only): partial.
NUMERICALLY_CONVERGED: not verified on new native jobs.
ETABS_OPENSEES_MATCHED: not verified.
EXPERIMENT_VALIDATED: not verified.
CODE_ACCEPTED: not verified.

No public native project data was committed. No automated approval of production material definitions or missing FSAM mappings. No complete M0–M6 result set is asserted. Further validation includes runtime benchmarks, Windows cancellation and full-record trials, exact model lineage across saved-case readers, gravity load and support-cut reconciliation, and nonlinear material qualification.
