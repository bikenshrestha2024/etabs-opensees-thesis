# expanded_workbench_tabs.py — eight-model integrated visual material workbench

**Source:** [components/validation/expanded_workbench_tabs.py](../../../../components/validation/expanded_workbench_tabs.py)

**Scope:** Adds Concrete02, ConcreteCM, SteelMPF and E-SFI/SFI numerical wall-source panels inside the established Tk workbench. The existing Concrete01/Steel02/FVD/BRB/wall response plots remain, and the full library tab opens 8-model editing/results, device recorder checks and measured FVD fitting.

**Inputs:** source cards from Material_Catalog, explicit measured CSV when supplied, active native OpenSeesPy environment (only when executing), and saved run folders. Default material inputs are illustrative. Any selected card is copied into an isolated new timestamped run directory.

**Outputs:** native subprocess report.json, response.csv, response.png, Parameter_Study.xlsx, run.log and optional measured comparison columns, from components.validation.parameter_studies. No application to building material definitions occurs.

**Research:** PEER Report 2015/12 Appendix B.3, Kolozvari et al. (2023), DOI 10.1016/j.engstruct.2023.116700, and OpenSees official material/element documentation. These references support benchmark formulations only. The actual nonlinear 25-storey building, material calibration and independent experiments are not verified by UI plotting.

**Tests:** tests/verify_expanded_workbench_tabs.py (source/card validation and CSV checks, solver-free); manually run 06_MATERIAL_DEVICE_VALIDATION.py in Windows Python 3.12 and perform native component runs for each tab.

[Source index](../../00_SOURCE_GUIDE_INDEX.md) · [Engineering gates](../../../00_THESIS_ACCEPTANCE_GATES.md)
