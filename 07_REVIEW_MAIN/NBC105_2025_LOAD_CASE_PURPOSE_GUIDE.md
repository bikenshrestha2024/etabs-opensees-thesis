# NBC 105:2025 — keep full-gravity and seismic-weight cases separate

**Official primary source:** Government of Nepal, Department of Urban Development and Building Construction, *NBC 105:2025 — Seismic Design of Buildings in Nepal*, §5.2, Table 5-1, printed p. 30.  
**PDF:** https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf  
**Classification:** confirmed official code wording; run-specific actual contributions/occupancy still require source verification.

## Which factors apply?

| Category | GRAVITY_1.0D_1.0L independent comparison | Seismic weight per §5.2 Table 5-1 |
|---|---:|---:|
| All dead/self-weight/finishes/partitions | 1.00 | 1.00 |
| Storage live | 1.00 | 0.60 |
| Other live | 1.00 | 0.30 |
| Roof live | 1.00 | 0.00 |

**When:** the first column is the project's requested full-unfactored gravity-only comparison; it is **not** a declaration that all gravity strength/service load combinations use these same coefficients. The second column governs seismic **weight/mass contribution**. Applicability of equivalent gravity preload in a response-history analysis must also be reviewed against the relevant analysis requirements (e.g., §8.1.1.2 / §9.3.1.2); do not equate mass and gravity-pattern coefficient blindly.

**Why:** 311,367.314 kN for `GRAVITY_1.0D_1.0L` and 286,419.758 kN for the configured Kobe seismic state **are different load scenarios by design**. Their difference is not a gravity error or ETABS mismatch. Compare each to ETABS with the exact same factors, load patterns, model/source, and support set. Gravity equilibrium within each case remains separate from ETABS/OpenSees physical equivalence.

**How and where in code:**
- `components/model/assembly.py::apply_gravity_profile` retains the existing `GRAVITY_1.0D_1.0L` profile and independently configured `AS_CONFIGURED` / `SEISMIC_SOURCE` profile; no model loads, masses or factors are automatically rewritten by the audit.
- `components/model/load_case_purpose.py` audits individual live categories, expected and applied gravity factors, and independent seismic mass factors, emits REVIEW_REQUIRED for unknown/mismatched categories, and names the purpose.
- `components/gravity/storey_loads.py` separately labels `storage_live_kN` in the source ledger instead of incorrectly grouping all live load into one occupancy column.
- Assembly prints `[LOAD CASE PURPOSE]` with profile, purpose, status, issue count and exact applied gravity/mass factors. That output is a **diagnostic report**, not an engineering pass.
- If an ETABS pattern name alone does not identify occupancy, document `seismic_load_categories` in the project configuration using `DEAD`, `STORAGE_LIVE`, `OTHER_LIVE`, `ROOF_LIVE`. These labels must be sourced from actual building occupancy and ETABS pattern assignments, not guessed by the program.

**Who:** researcher supplies verified load-pattern classifications and occupancy; structural/earthquake reviewer confirms appropriate NBC clause and comparison scenarios; software maintainer verifies code and tests.

## Acceptance and limitations

- Do **not** compare the two total support reactions as if they must agree numerically.
- Do compare **each case separately** with the source ETABS case, after matching boundary supports, physical model/EDB version, gravity P-Delta state and all contributing loads.
- `mass_factors` used for seismic inertia must preserve storage 0.60, other 0.30 and roof 0.00, even when gravity-only `gravity_factors` include 100% roof live.
- Unclassified or custom live patterns require documented explicit mapping; category heuristics are **not** project verification.
- Avoid double self-weight and check separate roof/live tributary distribution.
- A case-purpose match is **not** a soil/site, gravity load path, mass nodal mapping, ETABS equivalence, or overall code acceptance pass.

**Regression:** `python -m unittest discover -s tests -p 'test_nbc105_load_case_purpose.py' -v`. No native ETABS/OpenSees analyses performed in these tests.

## What this corrects in the original review

The prior review noted that gravity-only total load differs from the LTH preload. That observation is true, but it should **not be treated as evidence of a discrepancy**: the models intentionally use full versus seismic participation factors. The remaining engineering requirement is **like-for-like source comparison**, with the correct factor profile for each purpose.
