# NBC 105:2025 Annex B — seismic-link rotation acceptance

**Owner:** `components/nbc105/annex_b_steel_detailing.py`.

**Authority:** Annex B §§7.1.1–7.1.4, printed pp.95–97. These rules are **ONLY FOR QUALIFIED ECCENTRICALLY BRACED FRAME STEEL SEISMIC I-SECTION LINKS**.

**Rule:** Horizontal short/long link limits e≤1.6Mp/Vp and e≥3Mp/Vp; vertical short/long limits e≤0.8(1+alpha)Mp/Vp and e≥1.5(1+alpha)Mp/Vp. Rotation limit 0.08 rad short, 0.02 rad long and linear interpolation for intermediate. `alpha` is the smaller-to-larger end-moment ratio, 0–1. `seismic_link_rotation_limit_rad` returns only that limit, not a pass/fail of actual response.

**Explicit safety limitation:** A thesis SHS outrigger, BRB or FVD is not automatically a qualifying seismic link; the classification, steel material, section I geometry, axial force reductions, links/web stiffeners/connection strength and actual inelastic rotation require structural model and design verification.

**Tests:** `tests/test_nbc105_annex_ab_source_checks.py` (horizontal/vertical and wrong element type rejection).

## EBF I-section classification is mandatory

Annex B §7.1.1 printed p.95 restricts seismic links to **I-section geometry**. The reference calculator now requires `section_type='I'` or `'I-SECTION'` explicitly. SHS, FVD, BRB or generic project link objects are rejected rather than silently receiving the 0.08/0.02 rad limits. The input declaration alone still does not verify the actual exported section, link classification, material, axial reduction or demand rotation.
