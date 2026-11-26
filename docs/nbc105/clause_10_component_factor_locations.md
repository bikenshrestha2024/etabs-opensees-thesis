# NBC 105:2025: where ap, mu_p and Ip are stated (clause 10)

Date 2026-11-26 (owner ruling 5). Printed page numbers (PDF page = printed + 23 from printed p. 27). Source-to-code review only.

| Symbol | Notation list | Used in Eq. 10.3(1) (p. 49, symbol list on pp. 49-50) | Defining clause and table | Printed range / values | Code check |
|---|---|---|---|---|---|
| ap, component amplification factor | p. 6 | "ap = ... as per 10.3.1" (p. 49) | 10.3.1 and Table 10-1, p. 50 | "varies from 1 to 2.5"; 1.0 if \|T1-Tp\| > 0.5 s; 2.5 at \|T1-Tp\| = 0; linear between (0.5 s itself is not assigned in the table; the interpolation gives 1.0) | `component_amplification_factor`; `component_design_force` rejects ap outside 1 to 2.5 |
| mu_p, component ductility factor | p. 9 | "mu_p = ... as per 10.3.2" (p. 49) | 10.3.2 and Table 10-2, p. 50 | "varies from 1.5 to 2.5": 1.5 low deformability, 2.5 moderate; for high deformability a higher value "not exceeding 3.5 may be used if/as supported by research" | `component_ductility_factor`; `component_design_force` rejects mu_p < 1.5, and mu_p > 2.5 unless `research_supported_mu_p=True` (never above 3.5) |
| Ip, component importance factor | p. 7 | "Ip = ... as per 10.3.3" (p. 50, top) | 10.3.3 and Table 10-3, p. 51 | 1.5 for hazardous contents, life-safety function, storage open to public, emergency-facility continued operation; 1.0 for all other components | `component_importance_factor`; `component_design_force` accepts only 1.0 or 1.5 |

Related printed items: Eq. 10.3(1) and the list Z, Wp, hp, H on pp. 49-50; scope limit (component weight > 25 % of seismic weight) in 10.1, p. 49.

Tests: `tests/test_nbc105_followup_component_factors.py`. Module: `components/nbc105/clause_10_parts_and_components.py`.
