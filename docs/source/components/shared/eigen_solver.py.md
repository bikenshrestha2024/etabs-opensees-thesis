# eigen_solver.py — Modal eigensolver quality and large-model numerical control

**Python source:** [components/shared/eigen_solver.py](../../../../components/shared/eigen_solver.py)
**Current Git blob SHA:** e6470dfd8bdbdf54397fd905f189121a07d27de0
**Review status:** Source content was inspected for these specific behaviors. Physical/numerical validation not executed.

## What this file currently implements
Supports PythonSparse matrices and attempts native eigen backends with a PythonSparse fallback when a solver fails or returns incomplete eigenpairs; dense fullGenLapack is skipped above a model-size guard.

## Explicit assumptions and known deficiencies
A hanging native eigen call is not interrupted merely by fallback exception handling; use subprocess process isolation and cancellation. Reported modal mass participation alone does not validate nonlinear section/element behavior.

## Required thesis engineering changes
Include modal residual and Rayleigh damping sensitivity; log wall time and backend; compare actual ULS/SLS mode shapes and mass to ETABS; constrain native eigensolver runtime via a separate cancelable worker process.

## Cited scientific context
R10 and independent numerical eigenvalue verification; no paper citation is a substitute for checking assembled matrices.
References are indexed in [the research source register](../../../00_RESEARCH_REFERENCES.md). Paper citations establish appropriate model context, not code validation.

## Required regression output
Unit/metadata tests, isolated material or wall benchmarks, complete solver log, model+record hashes, type-safe status, full-record duration and independent ETABS/experiment comparison. Avoid marking a case verified if any gate remains unresolved.

[Source module index](../../00_SOURCE_GUIDE_INDEX.md) · [G00–G10 acceptance gates](../../../00_THESIS_ACCEPTANCE_GATES.md)
