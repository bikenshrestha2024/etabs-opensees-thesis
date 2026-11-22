# NLTHA readiness workflow: from template to a human-approved manifest

Scope: what to do when the nonlinear run stops with
"The selected file is an uncompleted readiness TEMPLATE ... Your nonlinear configuration also needs a reviewed material file and wall FSAM mappings". Nothing here approves a model. Approval is a human decision recorded in the manifest. Code never sets `approved_for_nltha` or any check to True.

## 1. What the dialog means

`_require_nonlinear_readiness` (`components/nonlinear_time_history/runner_and_gui.py`) runs before every nonlinear run. It stops when:

1. the manifest file is missing (`FileNotFoundError`; message unchanged);
2. `model_script` in the manifest is blank or a placeholder (the TEMPLATE case you hit);
3. the manifest is bound to a different model script;
4. the model script SHA-256 differs from `model_script_sha256`;
5. `approved_for_nltha` is not True;
6. any of the 16 check keys is not True:

```
etabs_topology_and_story_mapping_reviewed
wall_opening_and_coupling_beam_mesh_reviewed
wall_nonlinear_materials_and_reinforcement_cited_calibrated
frame_concrete_and_rebar_materials_reviewed
slab_and_diaphragm_idealization_compatible
area_and_frame_gravity_loads_reconciled_to_etabs
seismic_mass_reconciled_to_etabs_by_storey
support_conditions_and_foundation_assumptions_reviewed
is16700_initial_pdelta_plus_minus_cases_completed
p_delta_and_gravity_preload_completed
modal_periods_modes_and_mass_participation_reviewed
brace_fvd_brb_case_matches_selected_scenario
device_properties_cited_calibrated_or_devices_disabled
rayleigh_damping_and_device_damping_not_double_counted
single_element_and_wall_benchmark_checks_passed
record_pair_units_scales_and_nbc_limits_reviewed
```

Changing the checklist alone does not clear the material and FSAM part of the message. Those are separate configuration items (step 4).

## 2. See every blocker at once

`diagnose_nonlinear_readiness(config)` in `components/model/readiness.py` returns `{ready, blockers:[{code, message, fix}]}`. It is read-only. Codes: `model_script_missing`, `manifest_missing`, `manifest_unreadable`, `template_unbound`, `bound_to_other_model`, `model_sha_mismatch`, `not_approved`, `check_false:<key>` (one per false key), `material_file_missing`, `material_file_not_found`, `wall_fsam_tags_empty`, `parameters_not_reviewed`, `binding_not_recorded`, `model_config_changed`, `material_file_changed`, `wall_fsam_tags_changed`, `stale_runtime_copy`.

The gate keeps its original exceptions and messages and now appends this blocker list to each `RuntimeError`. The material, FSAM and `parameters_not_reviewed` blockers are reported in the list; for an unapproved manifest they do not add a raise (the 16 checks and approval decide). For an approved manifest the gate also raises on the input-binding blockers and on `material_file_missing`, `material_file_not_found`, `wall_fsam_tags_empty` and `parameters_not_reviewed` (section 5). `binding_not_recorded` is advisory only and never raises.

## 3. Create a model-bound UNAPPROVED draft

`bind_readiness_draft(template_path, model_script, out_path=None)` (non-GUI, same module) is what the readiness GUI `prepare` now calls. It copies the template, records the model path and SHA-256, and sets `approved_for_nltha` and every check to False. Default output: `OpenSees_Model_Readiness_Draft_<stem>_V134.json` beside the model.

- An existing unapproved draft already bound to the same model and SHA is returned unchanged, so human-saved evidence and checks are kept.
- A stale unapproved draft (model changed) is rebuilt with all checks False.
- An approved file is never overwritten; an unreadable existing file raises.
- A fresh draft still fails the gate with `not_approved` and all 16 `check_false:*` blockers. That is correct.

In the GUI (Prepare / inspect readiness checklist) the launch notice also lists open material, FSAM and parameter-review prerequisites. The notice code has not been run here (see Pending).

## 4. Material file and wall FSAM mappings (research draft only)

The gate needs `nonlinear_materials_file`, `nonlinear_wall_fsam_tags` and `nonlinear_parameters_reviewed` in `OpenSees_Complete_Model_Config_V118.json`. To get a starting point, use `components/nonlinear_time_history/material_draft.py` `prepare(source, destination, basis=...)`. It copies an assembled export, writes `Research_Wall_Parameters.json` and `Research_Wall_Materials.py`, sets the FSAM tags per wall property, and sets `nonlinear_parameters_reviewed` to False. The source export is not modified. The destination must not already exist.

The result is labeled `RESEARCH DRAFT; NOT PROJECT CALIBRATED OR APPROVED`. Values come from `material_source_sets.py` and the Material_Catalog, with references in `docs/00_RESEARCH_REFERENCES.md`:

| Ref | Use in the draft | Transfer restriction (from the reference table) |
|---|---|---|
| R01 Kolozvari, Orakcal, Wallace 2015, PEER 2015/12 | ConcreteCM/SteelMPF/FSAM web materials (Appendix B.3) | Do not import a PEER wall material card into all building walls as experimentally calibrated |
| R02 Kolozvari, Lopez, Massone 2023 | E-SFI-MVLEM-3D element formulation and benchmarks | Benchmarked shapes and loads are not equivalent to project openings, re-entrant core or connections |
| R05 Korkmaz and Kircil 2026 | Supplemental damping methodology (FVD) | Project damper stiffness, coefficient, exponent and installation must be demonstrated |
| R06 Ozkaya and Gurbuz 2026 | FVD arrangement sensitivity workflow | Composite-structure percentages are not predictions for the asymmetric RC building |
| R07 Guerrero Bobadilla et al. 2025 | BRB cumulative ductility and fatigue | Use actual BRB product geometry and tested protocol; DOI to verify |

These are PEER specimen and literature values, not project data. The draft's wall reinforcement (two curtains of 20 mm bars at 200 mm) is a placeholder layout, not extracted from drawings. FSAM geometry and reinforcement, 3D element constants, SHS properties and FVD/BRB parameters still need independent project sources.

Consequence for the checks: `wall_nonlinear_materials_and_reinforcement_cited_calibrated`, `frame_concrete_and_rebar_materials_reviewed`, `device_properties_cited_calibrated_or_devices_disabled` and `single_element_and_wall_benchmark_checks_passed` must stay False until you supply project evidence (reinforcement schedule, material tests or specification, device data) and review it. Having a draft file only removes `material_file_*` and `wall_fsam_tags_empty` blockers.

## 5. Human steps to approval

1. Run Prepare / inspect readiness to get the bound draft (step 3).
2. Create the research material draft (step 4), point the model config at it, and keep `nonlinear_parameters_reviewed` False.
3. Replace placeholders with project reinforcement and device calibration, with documents attached.
4. Complete each of the 16 reviews. Mark a check True only after its evidence exists.
5. Set `approved_for_nltha` True yourself, last. Any later change to the model script invalidates it (SHA mismatch).

Scope of the binding: besides the model script path and SHA-256, the manifest records three more SHA-256 values when a draft is bound (`bind_readiness_draft`) and when the readiness GUI saves or rebinds (`record_binding` in `components/model/readiness.py`):

| Manifest field | What is hashed | Gate blocker if it differs now |
|---|---|---|
| `model_config_sha256` | `OpenSees_Complete_Model_Config_V118.json` beside the model script | `model_config_changed` |
| `nonlinear_materials_file_sha256` | the resolved `nonlinear_materials_file` | `material_file_changed` |
| `nonlinear_wall_fsam_tags_sha256` | canonical JSON of `nonlinear_wall_fsam_tags` (key order ignored) | `wall_fsam_tags_changed` |

`nonlinear_materials_file_resolved` is stored for information and is not compared. A hash stored as `null` means the item was absent when recorded; an item that appears or disappears later also counts as a change. Values come from the run config when it carries the key, otherwise from the model config file, the same source `diagnose_nonlinear_readiness` uses.

Gate behavior, after the older checks have passed (so every older message is unchanged):

- A recorded hash that differs from the current file or tags raises `RuntimeError` naming the blocker. Re-review the change and save a new checklist; approval does not carry over.
- If `approved_for_nltha` is True and the material file is unconfigured or missing, or the FSAM tags are empty, the gate raises (`material_file_missing`, `material_file_not_found`, `wall_fsam_tags_empty`). An approved checklist with no material file is contradictory. The readiness GUI refuses to save an approval in that state. For an unapproved manifest these remain report-only.
- If `approved_for_nltha` is True and `nonlinear_parameters_reviewed` is not True, the gate raises `parameters_not_reviewed`. The value is read from the run config when it carries the key, otherwise from the model config file, so a run-config value overrides the model config. Approval with unreviewed nonlinear parameters is contradictory. An unapproved manifest still raises its older approval error first, and `parameters_not_reviewed` stays report-only there.
- An input file that exists but cannot be read (for example locked by another Windows program) is a blocker `binding_unreadable` in `diagnose_nonlinear_readiness` and raises `RuntimeError` in the gate and in `record_binding` / `bind_readiness_draft` (`BindingUnreadableError`). The check fails closed; it never crashes with a bare `OSError` and never approves anything.
- Research route: the gate has no research-profile switch, because the profile is chosen inside the model builder (`assembly.py`, `research_profile`), which takes its wall FSAM tags from the research profile and not from the config file. A manifest that was approved earlier for a research-route model with an empty `nonlinear_wall_fsam_tags` in the config now raises `wall_fsam_tags_empty` (and `material_file_missing` if no material file is configured). An approved research-route manifest whose `nonlinear_parameters_reviewed` is not True also raises `parameters_not_reviewed`; `assembly.py` skips that check for the research profile, so this is stricter than the model builder. This is intended: an approved NLTHA manifest must describe config inputs that exist. Remedy: put the reviewed wall property-to-FSAM mapping (and material file) in `OpenSees_Complete_Model_Config_V118.json`, for example from the step 4 research draft, then re-save the checklist. Research-route runs that are not production NLTHA should not carry an approved manifest.
- The gate's error text begins "NLTHA readiness binding check failed (approved manifest contradicts or no longer matches the model inputs)", which covers hash mismatches and the approved-manifest contradictions alike. Older manifests without the hash fields still pass the gate. `diagnose_nonlinear_readiness` reports `binding_not_recorded` (so `ready` is False) and the GUI notice lists it. Save the checklist once to record the hashes.

Readiness GUI: `prepare()` keeps an existing draft whose model-script SHA is unchanged, even when the config, material file or FSAM tags changed since approval. On launch the GUI therefore calls `rebind_if_binding_changed` (pure logic in `components/model/readiness.py`): if any recorded hash differs, approval and every check are reset to False, the current hashes are recorded, evidence text is kept, the file is rewritten, and a red notice lists the mismatch codes (`model_config_changed`, `material_file_changed`, `wall_fsam_tags_changed`). Save repeats the check, so inputs that change while the window is open also cannot be saved as approved. Legacy manifests without hash fields are not reset. The GUI wiring itself is PENDING a tkinter run.

Limits that remain: `nonlinear_parameters_reviewed` is enforced for approved manifests but is not part of the hash comparison except through the config file hash; files that the material file itself refers to are not hashed; and the hashes prove the files are unchanged since a human saved the checklist, not that their contents are correct.

## 5a. Stale runtime copies (guard in active code)

Saved projects can carry a frozen runtime copy such as `Saved_Project_V156/OpenSees_Runtime_V118/`. It is immutable evidence and is never edited or annotated. Its `runner_and_gui.py` still has the pre-gate readiness check (no blocker list, no input-hash binding) and its `application.py` opens the original EDB in place. The guard therefore lives only in active code: `detect_stale_runtime(path, include_children=False)` and `runtime_copy_notice(model_script)` in `components/model/readiness.py` (read-only; they work on paths that do not exist and write nothing).

Rule. The runtime root for a path is the nearest folder, walking up from the path (or its parent, for a file), that is named `OpenSees_Runtime_V<digits>*` or contains `components/nonlinear_time_history/runner_and_gui.py`. The copy is stale if any of these is true:

| Reason | Condition |
|---|---|
| `runner_source_missing` | `components/nonlinear_time_history/runner_and_gui.py` is absent |
| `runner_lacks_active_gate` | the runner text lacks any of `diagnose_nonlinear_readiness`, `format_readiness_blockers`, `gate_binding_blockers` |
| `readiness_module_missing` | `components/model/readiness.py` is absent |
| `readiness_module_lacks_fingerprint` | that file lacks any of `READINESS_CHECK_KEYS`, `def diagnose_nonlinear_readiness`, `def gate_binding_blockers` |

The markers are constants (`ACTIVE_GATE_RUNNER_MARKERS`, `ACTIVE_GATE_MODULE_MARKERS`); a test checks that the active tree passes its own fingerprint, so renaming one of them fails the test. A copy refreshed to the PR #124 gate but without the binding check is stale. This is a text fingerprint, not proof that two files are identical.

Where it shows up:

- `diagnose_nonlinear_readiness` adds the blocker `stale_runtime_copy` only when the selected model script lies inside such a runtime copy (ancestor folders only). It is reported, not raised by the gate: code running from the active tree is not the stale gate, and a model script that sits inside a stale copy is the case to fix by moving to active code.
- The readiness GUI launch notice also checks the `OpenSees_Runtime_V*` folders directly beside the model script (`include_children=True`) and shows a red warning, because the real V156 model script sits next to its runtime copy, not inside it. This is a warning only.
- Checked against the real `Saved_Project_V156/OpenSees_Runtime_V118/` as a read-only fixture: stale (`runner_lacks_active_gate`, `readiness_module_lacks_fingerprint`); the test also confirms no file there changed.

## 6. ETABS ingestion guards

These apply when converting an ETABS model (`components/ui/application.py`, helpers in `components/validation/gravity_etabs_direct.py`, `components/model/assembly.py`):

| Guard | What it refuses or records |
|---|---|
| Working copy | In the active `components/` code, ETABS opens a temporary copy of the EDB; the source EDB is not opened or modified. The copy is removed after ETABS exits (short bounded retry, then a logged warning; never raises). Runtime copies under saved projects are not covered; see section 8. |
| Units read-back | After setting units, the present units are read back; a mismatch raises instead of continuing in the wrong units. |
| Dropped points | Failed point-coordinate or point-diaphragm reads are collected and raise `DroppedPointsError`; no silent skipping. A nonzero trailing return code on a coordinate read now counts as dropped. |
| `assembly_errors` | Unparseable or nonzero-return material rows are recorded in the report's `assembly_errors`, which is fatal in the worker via `validate_converter_report`. |
| Connect failure | On failure after ETABS starts, the model is closed and ETABS exits; the original error is the one raised. |

## 7. What each kind of success means

| Result | Means | Does not mean |
|---|---|---|
| Solver success (run finishes, no divergence) | OpenSees converged for that model and record | ETABS equivalence, validated components, code compliance |
| ETABS equivalence | Mass, gravity, periods and geometry agree with ETABS within stated tolerance | The nonlinear components are valid |
| Component validation | Single-element and wall benchmarks pass against test data | Whole-building behavior or code acceptance |
| Code acceptance (NBC 105:2025) | Reviewed against clause limits (drift, torsion, record rules) by the responsible engineer | Anything about solver convergence |

No solver PASS is engineering acceptance.

## 8. PENDING (not run)

- Native Windows and ETABS COM runs of the Task 3 ingestion guards (OpenFile on the copy, present-units read-back, side-file cleanup, linked-file paths from the copy location).
- tkinter GUI behavior (readiness GUI prepare, launch notice including the stale-runtime warning, and the save/rebind code that records the binding hashes and refuses an unbindable approval); the sandbox has no tkinter. The shared helpers are tested headless.
- Refreshing or retiring the runtime copies under saved projects (for example `Saved_Project_V156/OpenSees_Runtime_V118/`, launched by `17_BUILDING_FULL_NONLINEAR.py`). They are not edited; they keep the pre-branch readiness gate and in-place EDB open. Section 5a only detects and warns (diagnosis blocker `stale_runtime_copy`, GUI notice); it does not stop someone launching the copy directly. The statement that the source EDB is not opened applies to the active `components/` code only.
- Full-model NLTHA on the project building.
- Project reinforcement schedule and FVD/BRB calibration.
- All 16 checks and `approved_for_nltha` remain False until you complete them.

Evidence notes: `engineering/agent_edits/20261120_nltha_readiness_gate.md`, `engineering/agent_edits/20261120_etabs_ingest_guards.md`, `engineering/agent_edits/20261120_nltha_binding_runtime_guard.md`.


## 6. Screenshot (2026-11-22): 20 blocker items and readable remediation

The legacy GUI's long `Input needs review` message showed **20 unresolved blockers** (16 `check_false` source reviews, 1 `not_approved`, `material_file_missing`, `wall_fsam_tags_empty`, `parameters_not_reviewed`). This is a **preflight refusal**, not an OpenSees Newton iteration or wall convergence error. Correct physical-model gating must never be disabled simply to avoid the dialog.

The source GUI now opens a **scrollable review dialog** instead of squeezing these items into a narrow one-button message box. It groups checks into Human Approval, Engineering Checklist, Model Materials and Model Input Binding, and provides **Open model-bound checklist**, **Copy blockers**, **Save report locally**, and **Close**. Saving produces a plain text report in the operator-selected local path; no source EDB, model config, material data or human approval is changed. The original `_require_nonlinear_readiness` still rejects the run before allocating the output case or starting the solver.

The UI also correctly labels a requested `trial_duration_s=0` **Suite** (full-record request) rather than `Trial`; a positive duration is `Trial`. This is a directory/scope bug fix, **not** evidence the full physical record has solved.

**Action on current export:** Open **Prepare / inspect model-bound readiness checklist**. Supply independently reviewed project material definitions and section-specific FSAM tags, then verify the 16 checks with source-linked notes. A research-only PEER material *draft* can help isolate a numerical wall failure but it is not an acceptable project production material calibration. The independent [Stage 38 runbook](programs/38_DIRECT_EXISTING_MODEL_NLTHA.md) describes source-bound exploratory full XY/YX execution, not a bypass of this production approval.

See [NLTHA screenshot and source review](../REVIEW_MAIN/06_NONLINEAR_TH/20261122_NLTHA_READINESS_AND_GUI_SCOPE_SOURCE_REVIEW.md).

## 7. 2026-11-22 — complete 21-gate source and evidence register

The 21 current blockers are **1 human approval, 16 source/model checklist items, 3 material/FSAM/calibration configuration items, and 1 unbound-template pointer**. The 40-mode elastic/ULS MRSM data is numerical evidence, not independent native ETABS equivalence or approval of nonlinear RC properties. Use [the complete 21-item closure plan](../REVIEW_MAIN/06_NONLINEAR_TH/20261122_21_BLOCKERS_CLOSURE_PLAN.md) before marking any check true. **NEW:** Auto-filled `AVAILABLE FOR REVIEW:` and `INPUT / REVIEW REQUIRED:` labels are *not* acceptable evidence references when saving checked items. Approval also requires `nonlinear_parameters_reviewed=true` in the source model configuration; neither the GUI nor this documentation sets that value for a reviewer.


## 2026-11-22 — direct PEER Appendix B.3 literature-baseline policy

The user's thesis uses directly cited published constitutive inputs as a **research** baseline and reports source-specific parameter sensitivity; separate project material testing is **not** a prerequisite for attempting exploratory NLTHA. The PEER RW-A15-P10-S78 web FSAM reinforcement ratios are now directly adopted as `rho_x=rho_y=0.0074`, with published `nu=0.8` and dowel `alpha=0.01`. Its **distinct** boundary values (`rho_x=0.0082, rho_y=0.0587`) remain recorded, NOT applied to arbitrary wall panels without a verified region map. In the isolated PEER research draft, the former invented `20 mm @ 200 mm` bar proxy no longer controls these web values; mixed/nominal sensitivity bases remain labeled assumptions. See [the full page-specific source/units table and methodological distinction](https://github.com/bikenshrestha2024/etabs-opensees-thesis/blob/main/docs/engineering/20261122_DIRECT_PEER_LITERATURE_NLTHA_PARAMETERS.md).

Source-level tests: `tests/test_peer_direct_literature_fsam_transfer_20261122.py`. This does not certify that the 25-storey X-wall first step converged, establish actual M0–M6 device input, or set `approved_for_nltha=true`.
