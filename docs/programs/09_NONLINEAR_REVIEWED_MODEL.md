# 09 — Reviewed nonlinear model workflow

**Entry point:** [`09_NONLINEAR_REVIEWED_MODEL.py`](../../09_NONLINEAR_REVIEWED_MODEL.py)  
**Category:** Nonlinear analysis and verification  
**Status:** Documentation and route guide only; runtime execution not performed by this change.

## Purpose
Reviewed nonlinear model workflow. This launcher is an entry point, not necessarily the implementation itself. See the exact imported calls in the linked Python file before changing the backend.

## Required inputs
Reconciled geometry, reinforcement, materials and validated component inputs. Confirm paths, units, configuration assumptions and project-specific datasets in the active script/GUI. Do not assume a file from another release is compatible.

## Main implementation references
- `components/nonlinear_time_history/`
- `Research_Components/02_MODELLING_BASIS.md`

## How to run
1. Work from the complete repository in the configured Windows Python/OpenSeesPy environment; keep component directories together.
2. Open `09_NONLINEAR_REVIEWED_MODEL.py` in Spyder and run it, or invoke `python 09_NONLINEAR_REVIEWED_MODEL.py` from the repository root where suitable. For this diagnostic launcher, inspect its command-line arguments and usage before running.
3. Select/provide the appropriate export and input files when the script requests them; verify report paths before assuming output files were created.
4. Preserve a copy of inputs, commit ID, parameter register, OpenSeesPy version, and complete solver log.

## Expected results
Nonlinear input audit and transient outcomes. Exact filenames and behavior depend on the current implementation and selected case. Check output existence, finite values and completion status independently.

## Validation / stop gate
**Hold full-building performance claims until full records converge and component benchmarks pass.** Record pass, fail, skipped, and unresolved separately. A GUI launch, gravity pass, or partial transient step is not a completed calibrated NLTHA.

## Known limitations and improvement backlog
- Trace launcher -> backend function -> imported modules -> output file with an automated, versioned dependency manifest.
- Add reproducible command-line smoke tests and validate the user-selected folders before launching heavyweight analyses.
- Report executable version, input hashes, units, runtime configuration, exceptions, and solver termination reason per run.
- Keep historical evidence read-only; do not silently rewrite or delete results when organizing folders.

[Program index](00_PROGRAM_INDEX.md) · [Project handoff](../../START_HERE_V167.md) · [Modeling basis](../../Research_Components/02_MODELLING_BASIS.md)
