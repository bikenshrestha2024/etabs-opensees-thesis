# 2026-11-17 — Short-run timing metadata missing on failure

**Source inspected:** components/shared/timing.py, timed_outputs wrapper; test tests/test_timing_metadata_structure.py. No ETABS/OpenSees physics files altered.

## Confirmed root cause

The wrapped stage previously filtered created files using file.stat().st_mtime_ns >= time.time_ns() captured before execution. Real filesystems can have coarser timestamp precision, clock rounding, or minor skew: a newly written file can have an mtime just before the captured threshold. This occasionally hid newly written failure artifacts from 00_PROCESSING_METADATA/ARTIFACTS, including the observed CI failure when expecting partial.json.processing.json for a failing stage. This was not a missing solver result, but a missing **evidence-status sidecar**.

A deterministic regression patches time.time_ns to 10**20 while writing new_failure.json then throwing RuntimeError. The original implementation fails to record the new artifact. Existing tests cover nested output discovery, repeated runs without duplicate status files, and explicit StageTimer behavior.

## Correction / scope

The timed_outputs wrapper snapshots eligible files with (mtime_ns, size) **before** the operation and again after, classifying all new paths as changed independent of timestamp epoch. Modified existing outputs are recorded when size or mtime changes; unchanged historical files are not attributed to the current stage. The original exception still propagates. Sidecars stay in the canonical 00_PROCESSING_METADATA/ARTIFACTS tree, preserving source JSON/CSV schema and original output bytes.

Caveats: a path overwritten with equal size and identical preserved mtime cannot be detected by metadata alone; and snapshotting many files adds read-only directory enumeration overhead. A native Windows run with the user's large export should benchmark this. No source mass, stiffness, mesh, support, damping, modal, gravity or NLTHA calculations changed.

## Acceptance

- RED then GREEN deterministic failure-path test.
- Existing timing metadata regression tests pass on the exact PR SHA.
- Integrated source audit references exact updated source Git blob and this report.
- Native Windows large model performance and ETABS/OpenSees engineering checks remain OPEN.
