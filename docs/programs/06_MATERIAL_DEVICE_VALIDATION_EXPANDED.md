# Unified visual material/device workbench

Run `06_MATERIAL_DEVICE_VALIDATION.py` from your full Spyder/conda-forge Python 3.12 checkout. The original Concrete01 / Steel02 / FVD / BRB / Walls / Steps and citations / Run log tabs remain. Four additional graph-enabled material panels are embedded in the SAME interface:

- Concrete02: compression cycling, tensile cracking, unloading; actual source/reference cards.
- ConcreteCM: confined/unconfined material law and specimen profiles (including PEER web values).
- SteelMPF: symmetric/unequal yield and cyclic transition source cards; preserve the distinction between paper Appendix cR1=18.5 and author example .925.
- E-SFI / wall materials: 3D E-SFI numerical patch and measured specimen/source selection, without claiming full core experimental validation.

Each new tab displays source and citation, full parameter JSON, native material commands, runs the existing isolated native parameter study, plots hysteresis plus response history, opens saved outputs, and offers the existing tuning/measurement and animation/GIF tools.

The Full library / calibration tab launches complete 8-model parameter cards and results viewers, the native FVD/BRB recorder benchmark, and Maxwell FVD measured-data fit. Source values are not approved for your building. All new outputs use timestamped folders; existing V149 results remain unchanged.

This addition extends the GUI, not the actual physical validation state. Test with `python tests/verify_expanded_workbench_tabs.py`, then manually launch on Windows and run native Concrete02/ConcreteCM/SteelMPF and E-SFI components. See PEER Report 2015/12 and Kolozvari et al. (2023), DOI 10.1016/j.engstruct.2023.116700.
