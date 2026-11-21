# NBC 105:2025 Annex A — RC wall minimums

**Owner:** `components/nbc105/annex_a_rc_detailing.py`.

**Authority:** Annex A printed §§5.1, 5.3 and 5.5, pp.76–79, uploaded NBC 105:2025. Source read directly from the user-uploaded code.

**Pure rule helpers:**
- `rc_wall_detailing_minima`: special RC walls 150 mm or more, **coupled shear walls 300 mm or more**, wall length/thickness >=4, horizontal and vertical reinforcement >=0.0025 of gross area, minimum two curtains where thickness>=200 mm or shear stress>0.25√fck, bar diameter<=tw/10, bar spacing<=min(lw/5,3tw,450 mm).
- `rc_wall_boundary_element_requirement`: gross-section extreme compressive stress **>0.2 fck** requires boundary elements; each end zone length 0.2lw, boundary reinforcement 0.8%–6% (practical upper 4%). Boundary elements may be discontinued where compressive stress <0.15 fck, subject to full engineering review.
- `coupling_beam_diagonal_required`: compares shear stress to the Annex A §5.5.2(a) diagonal-reinforcement threshold **0.1√fck (Ls/D)**.

**Units:** Length/spacing/bar diameter in mm, stress and fck in MPa, reinforcement as a fractional area ratio. Code rejects nonfinite and physically invalid inputs.

**Scope:** These are rule lookup/threshold calculations. They do not prove full member shear/flexure capacity, confinement, diagonal reinforcement bar area, bar anchorage, wall openings §5.6 or structural coupling. A 12 m gross envelope with openings cannot be marked fully code-compliant using these helpers alone.

**Tests:** `tests/test_nbc105_annex_ab_source_checks.py`. No native RC rebar or ETABS file uploaded.

## §5.6 opening reinforcement checklist (source printed p.79)

`rc_wall_opening_rebar_review` compares each side's additional vertical/horizontal reinforcement to at least half the respective interrupted steel area; it checks explicit confirmations that vertical bars extend full storey, horizontal bars receive development length beyond the opening and shear strength is checked at critical horizontal planes through openings. **Boolean declarations are not proof that construction or reinforcement drawing has been verified.** The function makes no combined shell/pier coupling or member-capacity acceptance claim.
