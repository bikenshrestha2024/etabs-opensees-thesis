# Exact research source values — RW-A15-P10-S78 Appendix B.3

In PEER Report 2015/12 Appendix B.3 (printed pp. 89–91, PDF pp. 102–104), the reproduced 2D SFI-MVLEM model uses:

- Height 72 in, thickness 6 in, width 48 in, vertical nodes at 0, 12, 24, 40, 56 and 72 in; five segments.
- Five section macrofibers, widths 9/10/10/10/9 in. Confined outer macrofibers and three unconfined web macrofibers.
- Longitudinal boundary steel SteelMPF fy=69.0 ksi and b=0.005. Web and X steel fy=58.4103 ksi, b=0.02; E=29,000 ksi; transition R0=20, cR1=18.5, cR2=0.0015 as **printed in Appendix B.3** (not the software documentation example's 0.925).
- Unconfined ConcreteCM fpc=-8.09 ksi, epsc0=-0.002371, Ec=5403.2172 ksi, rc=15, xcrn=1.022; confined boundary ConcreteCM fpcc=-10.479723 ksi, epsc0=-0.005873, Ecc=5953.9187 ksi, rc=12.072964, xcrn=1.023; both share ft=0.335798 ksi, et=0.00008, rt=1.2, xcrp=10000.
- FSAM web reinforcement rhoX=rhoY=0.0074; boundary rhoX=0.0082, rhoY=0.0587, friction nu=0.8 and dowel alpha=0.01.
- Appendix prescribed axial load 149 kip in the paper model.

The JSON source card stores all of these as **paper benchmark inputs**. The Python reader converts paper ksi to model kN/m² exactly once. Neither the paper's reported confined peak strength nor longitudinal steel density is assigned to your building's core or columns, because actual cage detailing and axial loading differ. Reproduce the paper model's cyclic response against laboratory data before claiming calibration. The author used **2D** SFI-MVLEM; adapting it to your 3D E-SFI-MVLEM-3D remains a separate modeling/validation question.

Source: https://peer.berkeley.edu/sites/default/files/webpeer-2015-12-kristijan_kolozvari_kutay_orakcal_john_wallace.pdf
