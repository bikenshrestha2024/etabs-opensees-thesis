# Paper-sourced reinforcement and confinement — separate specimen registry

This register transcribes measured specimen descriptions from **PEER Report 2015/12**, Sections 3.2.1–3.2.2 and Appendices B.2/B.3. It is intended for stand-alone calibration of RW2 and RW-A15-P10-S78, not a substitute for actual project reinforcement.

| Specimen | Dimensions | Boundary | Web | Axial load |
|---|---|---|---|---|
| RW-A15-P10-S78 | 48 × 72 × 6 in | four #5 plus four #6 A706 Grade 60 | #3 Grade 60 @ 5 in in X/Y | ~10% wall axial capacity |
| RW2 | 48 × 144 × 4 in | eight #3 Grade 60 | two curtains #2, reported fy=65 ksi | ~7% |

RW-A15-P10-S78 was represented with 5 vertical SFI-MVLEM elements, 5 section macrofibers (2 confined outer boundary, 3 unconfined web), with bottom two segments 12 in high. Concrete strength from test cylinders 8.09 ksi. RW2 had 16 height MVLEM segments and 8 cross-section fibers, and its report benchmark is flexural-only with large modeled shear stiffness.

**Critical limitation:** Confinement strength, hoop pitch, effective core and steel hardening parameters must come from Appendix input/model cards and original specimen drawings. Narratively reported reinforcement count is insufficient to generate a physically calibrated fiber section. The exact appendix source must be replicated before marking it verified. No code has been authorized to apply these bars to the high-rise RC core or columns.

Files: [source data](../../Research_Components/paper_specimens/PEER_2015_12_WALL_SPECIMENS.json) · [validator](../../components/nonlinear_time_history/paper_specimen_sources.py). Source: https://peer.berkeley.edu/sites/default/files/webpeer-2015-12-kristijan_kolozvari_kutay_orakcal_john_wallace.pdf .
