# 00 — RTFC implementation instructions for repository contributors

Read [the RTFC prompt](../../.github/prompts/soil-c-nltha-rtfc.prompt.md).
The training slide's ordering is **R = Role, T = Task, F = Format,
C = Context**, not a new seismic code or numerical algorithm.

### Example task-specific applications

| Subprogram | Task to append to RTFC | Evidence required |
|---|---|---|
| 01–10 ETABS import / 3D model | Audit mass, diaphragm, element geometry, core openings and actual reinforcement, without generating fictitious rebar | ETABS import log, model hash, geometrical and force-balance checks |
| 11–20 gravity/modal/response | Validate gravity and P-Delta before eigen and NLTHA; calculate 90% X/Y cumulative mass and justify damping modes | Gravity reactions, eigenvalue output, exact mode references, model hash |
| 21+ wall diagnostics | Reproduce element-level earliest nonfinite wall force at first step, preserve traceback; isolate ZERO/X/Y probes | Actual failed time, element and node tags, recorder traces, accepted steps |
| 32–36 ground motions | Audit eight pairs and both XY/YX orientations with unchanged Soil C matched `Acc(g)` and one unit conversion | Paired SHA256 and exact Path factors, records, dt, Gorkha/Loma decisions |
| 37+ thesis cases | Run M0–M6 only when source/model/gating evidence is complete; keep SLS/ULS and each orientation independent | Full histories, output signatures, physical acceptance checks |
| Materials FVD/BRB/FSAM | Validate independent experimental reference material cards and native device behavior | Paper ID, specimen geometry and actual measured curves, calibrated parameters and energy signs |

### Code review template

```text
R: Structural dynamics engineer + skeptical Python reviewer.
T: Review exactly one named source module. Identify one P0 defect,
   implement a smallest safe fix with a failing regression first.
F: Summary; exact diff; clauses/citations; test log; unresolved
   native/building validation; commit SHA.
C: NBC 105:2025 Soil C RC dual 25-storey asymmetric building,
   eight already-matched A/B pairs; do not double scale;
   use current model, preserve source hashes, no fabricated approvals.
```

### Distinguish engineering evidence

- **STATIC_VERIFIED**: source fingerprints, consistent config/schema,
  bounded numeric formula or Python regression.
- **NATIVE_NUMERIC_VERIFIED**: OpenSees executable actually analyzed
  required case and returned independently checked finite outputs.
- **EXPERIMENTALLY_VALIDATED**: cited experimental specimen
  and numerical response reproduced to a declared acceptance protocol.
- **NBC_DESIGN_REVIEWED**: actual project design inputs, full response,
  code clauses and documented qualified reviewer interpretation.

One status does not imply another. Keep project-private ETABS and seismic
records local; only commit safe metadata, source code and comments.
