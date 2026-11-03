# paper_specimen_sources.py — PEER paper specimen material source register

**Source:** [components/nonlinear_time_history/paper_specimen_sources.py](../../../../components/nonlinear_time_history/paper_specimen_sources.py)

**Purpose:** Load and verify paper-sourced specimen input registers, including RW2, RW-A15-P10-S78 and the PEER Appendix B.3 ConcreteCM/SteelMPF/FSAM benchmark values, with carefully documented source units and explicit non-transfer to the actual asymmetric high-rise building.

**Inputs:** JSON paper specimen cards in [Research_Components/paper_specimens](../../../../Research_Components/paper_specimens), including `PEER_2015_12_WALL_SPECIMENS.json` and `PEER_2015_12_RW_A15_B3_SFI_INPUTS.json`. Published Appendix B.3 uses inch/kip/ksi units. The exact-valued adapter converts ksi into kN/m² once.

**Checks:** finite physical dimensions and correct specimen ID, named confinement regions, five 9/10/10/10/9-inch macrofibers, documented SteelMPF reversal parameters, negative compression convention and `project_transfer_approved: false` flags.

**Outputs and status:** return paper-test benchmark cards and source-provenance metadata. **No actual building frame or wall bar schedules are changed**; no experimental loop replication is implied.

**Citation:** Kolozvari, Orakcal & Wallace, PEER Report 2015/12, Appendix B.3 and Section 3.2.

**Validation:** `tests/verify_peer_b3_materials.py` and source-coverage tests; native cyclic comparison against the experimental specimen remains required.

[All component guides](../../00_SOURCE_GUIDE_INDEX.md) · [Research references](../../../00_RESEARCH_REFERENCES.md)
