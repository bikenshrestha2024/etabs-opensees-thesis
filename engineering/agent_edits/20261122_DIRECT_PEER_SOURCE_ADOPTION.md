# Agent change log — PEER 2015/12 direct literature input

**Date:** 2026-11-22. **Actual agent:** ChatGPT GPT-6 with connected GitHub API and public PEER paper lookup; no local Windows or ETABS/OpenSees native execution.

## Read-first engineering contract

- `AGENTS.md`, `engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md`, `.agents/skills/etabs-opensees-read-first/SKILL.md`, `engineering/rules/CORE_RULES.md`, `engineering/rules/ENGINEERING_GATES.md`, `engineering/migration/README.md`, `docs/programs/00_PROGRAM_INDEX.md` were actually read.
- GitHub main baseline when branch created: `cd1cbc9c9b88055732ed943b65d72c22b1d88a81`; feature branch `fix/peer-literature-direct-rho-material-transfer-20261122`.
- ETABS source SHA/EDB, current model ZIP source, native paired wave SHA, and client Windows executable unavailable in connected GitHub view. **No source EDB or private workbook was copied/edited.**
- **PHYSICAL:** exactly 32 primary foundation supports + 44 other wall mesh points with transfer not independently validated. **WALLS:** 2×12 m X-direction walls with openings and 3×6 m solid Y wall lines. **GRAVITY comparison:** `GRAVITY_1.0D_1.0L` vs separate NBC 105:2025 §5.2 seismic weight. **State:** M0–M6, ULS/SLS independent.
- **Change:** use actual PEER Appendix B.3 web `rhoX=rhoY=.0074` directly for literature research paths; preserve original separate boundary FSAM option, no fabricated boundary geometry, no change to production approval flags or Source EDB. The solver and E-SFI 3D element are unchanged.
- **Reference:** Kolozvari, Orakcal & Wallace, PEER 2015/12 Appendix B.3, printed pp. 89–91 (web and boundary cards); secondary 2023 E-SFI-MVLEM-3D article DOI 10.1016/j.engstruct.2023.116700; optional Yang et al. 2021 FVD trial DOI 10.1155/2021/6673682.
- **Owners and readers:** `components/nonlinear_time_history/material_source_sets.py`, `material_draft.py`, `research_building_materials.py`, Stage 38 direct existing model, Material Source Table GUI and research evidence reports. `components/model/readiness.py` production approval semantics intentionally unchanged.
- **TDD:** the initial GitHub CI on test-only commit `374e30e047d3e5e6d559cb571038bb5e08a18e42` failed because the expected helper `peer_fsam_panel_values` did not exist; implementation then added, regression expanded to cover source value table, draft status and direct-building path.
- **Source status:** published numbers are directly attested to one specimen; the uniform research web assignment is an **analyst transfer decision** for the 25-storey model. Nominal M30/Fe500 and mixed-source bases remain separately identifiable. A ±10% sensitivity perturbation is an analyst bracket, not a published interval.
- **Test and acceptance:** GitHub CI checks are to be read from final PR head before claiming success. The 25-storey native XY/YX Kobe record, first-step X-wall convergence, project-specific configuration, ETABS/OpenSees nodal reactions and live device/damping response were **not rerun**. No thesis design or experiment qualification asserted.

See `docs/engineering/20261122_DIRECT_PEER_LITERATURE_NLTHA_PARAMETERS.md` for numerical values, exact printed-paper citation, stress and damper coefficient conversions.
