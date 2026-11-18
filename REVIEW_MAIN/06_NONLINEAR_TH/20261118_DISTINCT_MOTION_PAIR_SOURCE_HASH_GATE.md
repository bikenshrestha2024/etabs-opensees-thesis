# 2026-11-18 — M0–M6 comparison cannot count repeated earthquake source bytes as independent events

**Status:** Confirmed source-level data-integrity defect with test-first reproduction. **Not** an executed native OpenSees analysis or an independently verified earthquake record suite.

## Root cause and evidence

The `components/nonlinear_time_history/variant_comparison.py::compare_completed_cases` function matched `record_sha256` between M0 and M1–M6 for each case and checked XY/YX orientation identity within the same event. It did **not** check whether **different** earthquake `pair_id` values within one limit state used identical source hashes. Consequently a study could report 3 or 8 nominal event pairs while reusing a single matched waveform pair, giving an invalid independent-event sample count and misleading aggregation. The comparison still returned `RESEARCH_SCREEN_ONLY_NOT_THESIS_VALIDATION`, but it allowed this flawed input into its numerical screening.

**RED:** [GitHub integrated audit 44259116373](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/44259116373), test-only commit `342cfe1618132a850f5e2465775caca95e778d90`, `test_reject_two_pair_ids_with_identical_motion_source_hash` failed with `AssertionError: ValueError not raised`.

## Minimal correction

For each of ULS and SLS separately, collect each source's SHA-256 from the M0 reference cases using canonical hexadecimal case; reject any same digest assigned to **different** `pair_id` values. The already established across-M0–M6 and XY/YX identity and accepted-time-duration checks remain unchanged. Synthetic seven-pair test fixtures P4–P7 now use distinct synthetic SHA strings instead of silently reusing P1, so older aggregation semantics can be tested independently of source-aliasing.

**Interpretation:** A SHA value in a report is *claimed provenance*, not proof that the original file bytes were read. Final use requires independent hash calculation from source waveform bytes, unambiguous two-component pair representation, verified scaling/units/sampling `dt`, the original SeismoMatch matches and relevant Gorkha/Loma exceptions. Distinct hashes alone cannot qualify the suite. This guard also does not establish that seven structural variants contain correctly different models.

**GREEN:** require exact code-commit passing integrated repository audit, test suite and NLTHA quality workflows before merge. Reattest both source-inspected functions `validate_variant_manifest` and `compare_completed_cases` to the exact new Git blob whenever this module changes; their review state remains `SOURCE_INSPECTED_TESTED_NOT_NATIVE_VERIFIED`.

## Engineering validation still OPEN

1. Full source-level semantic inspection of approximately 4,424 previously inventoried code units remains unfinished; the canonical ledger tracks narrow tested functions only.
2. ETABS↔OpenSees physical equivalence remains unverified: original 76-source-restrained model's 44 additional wall nodes carry about 104,463 kN in OpenSees while ETABS point-object FZ is zero. Obtain native analytical-joint/MPC/6-DOF force and wall physical-cuts; 32 and 97 remain distinct sensitivity cases.
3. Nonlinear wall element 110280/112778 first-step X-only transient failure remains unresolved. Native coupon/panel/connected-bay validation and X/ZERO/Y/XY tests with last accepted/first failed state are necessary.
4. The eight event pairs × seven variants × two limit states × two XY/YX orientations require 224 native *complete full-duration* responses, with true source hashes, timestep convergence, damping/element/device energy, model geometry and physically reviewed demand metrics. Configuration files and static checks never satisfy this gate.

No source EDB, user-restricted waveform, PDF, executable, material parameters or native engineering results were modified or uploaded by this fix.
