# 02 — NBC 105:2025: formula, source citations, and actual model validation

Updated: 2026-11-13. **This is a navigable engineering reference and evidence register, NOT a certification of the current ETABS/OpenSees model.** Each claim below must be traced to the indicated code/source and current assembled inputs. Source code may contain a reference while the numerical model implements a different effective value. Obtain approval of the governing project design basis.

## Reference source register

| Source | URL | Relevant use | Evidence status |
|---|---|---|---|
| Nepal National Building Code NBC 105:2025, *Seismic Design of Buildings in Nepal* | https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf | Seismic weight, stiffness, design spectra, seismic action and drift provisions | Official document cited in project; verify downloaded edition, page and amendment |
| IS 16700:2023, *Criteria for Structural Safety of Tall Concrete Buildings* | https://www.services.bis.gov.in/ | Supplementary conventional-slab effective stiffness and project initial P-Delta case basis | Verify official text and suitability; not an NBC replacement |
| OpenSeesPy ShellMITC4 | https://openseespydoc.readthedocs.io/en/latest/src/ShellMITC4.html | 4-node shell, 3D/6 DOF, compatible section | Public technical documentation |
| OpenSees rigidDiaphragm | https://opensees.github.io/OpenSeesDocumentation/user/manual/model/mp_constraint/rigidDiaphragm.html | In-plane kinematic constraint; does not create physical slab load-path bending | Public technical documentation |
| CSI ETABS Analysis Reference Manual | https://docs.csiamerica.com/manuals/etabs/Analysis%20Reference.pdf | Shell and frame modeling, offsets, meshing, stiffness/loading conventions | Manual; verify local ETABS major release |

## Code reference versus physical implementation

### NBC §5.2 / Table 5-1 — Seismic weight

For each story, classify occupied live load before applying factors. The project audit states: 100% dead, 60% storage live, 30% other live, 0% roof live. Review the exact occupancy allocation and nonstructural dead components in the current source model before adoption.

`W_i = D_i + 0.60 L_{storage,i} + 0.30 L_{other,i} + 0 L_{roof,i}` (symbolic project interpretation; independently verify code and loads). Seismic mass in compatible SI units is `m_i = W_i/g`, with g defined consistently with solver length units and mass formulation. A *seismic weight ledger* is not, by itself, an analysis-specific **static P-Delta gravity combination**. Document separate choices for: (a) 1.0D+1.0L gravity comparison, (b) sustained gravity preload for NLTHA, (c) ULS/SLS combinations and (d) seismic mass. Never compare case totals as equivalent if factors differ.

### NBC Table 3-1 — Effective stiffness review

Reference values recorded in the current project (ULS/SLS, multiplied by the specified flexural property as applicable):

| Component | ULS | SLS | Review condition |
|---|---:|---:|---|
| Beam | 0.35 | 0.70 | Verify local bending axes and source modifiers |
| Column | 0.70 | 0.90 | Verify axial-flexural coupling and end zones |
| Cracked RC wall | 0.50 | 0.70 | Check wall in-plane effective flexure; shell slab bending modifier alone does not cover it |
| Uncracked RC wall | 0.80 | 0.90 | Define cracked/uncracked classification |
| Masonry wall | 0.45 | 0.60 | Applicability depends on physical modeled participation |
| Steel | 1.00 | 1.00 | Verify gross member section and any physical reduction |

**Conventional RC slab:** Project supplemental IS 16700:2023 Table 5 values 0.25 ULS / 0.35 SLS must be verified against the intended slab type. Do **not** silently take NBC Table 3-1 *flat slab* 0.25/0.50 factors for a beam-supported slab. The elastic shell section's membrane stiffness, bending stiffness, self-weight and mass are distinct quantities; document each.

Open the actual assembled model data, stiffness configuration and generated commands. Record a table: property/object, ETABS source value, specified effective modifier, resulting ETABS property, generated OpenSees property, solver units, evidence filename/hash, and percent discrepancy. No numerical equality is claimed here.

### IS 16700:2023 §7.2(d) — project initial P-Delta gate

The project's prerequisite is four signed X/Y `1.2 DL + 0.5 IL ± 1.5 EL` cases (and wind variants where applicable). They remain labelled as IS-based initial cases, not NBC load combinations. Actual successful solver convergence, gravity state, full model/source identity, selected sign/axis, stiffness and reactions must be recorded for **each** case before the gate is marked reviewed. The initial static P-Delta case is different from sustained NLTHA gravity preload.

### NBC §§5.5.3, 6.5, 7.5, 8.1.1

Project reference drift ratios: ULS 0.025, SLS 0.006; model must export per-story signed drift, envelope critical-time state, status and code action basis. Review nonlinear drift versus elastic displacement amplification and distinguish MRSM force scaling from drift scaling.

Rayleigh viscous damping: for chosen modal angular frequencies \(\omega_1, \omega_2\) and target \(\zeta\), solve \(\zeta(\omega)=a_M/(2\omega)+b_K\omega/2\). Report the two selected frequencies, coefficients, damping ratios over all retained modes and any >5% screening alerts. Do not double-apply a stiffness modifier to nonlinear fiber stress-strain or incorrectly include damping in nonlinear dissipative devices.

### NBC ESM / MRSM / NLTHA

ESM formulas and comparison plots are for the correct code applicability conditions; this project's approximately 25-story high-rise currently labels ULS ESM as **comparison only**. Never relabel an ESM comparison as accepted seismic analysis. For the equivalent static force profile, record adopted directional period, site soil classification, zonation, importance, ductility/overstrength factors, total seismic weight, spectral coefficients, base shear and story distribution. Explicit accidental eccentricity must be checked against mass center and stiffness center, not inferred from six exported signatures alone.

Current gap: measured Vs30 evidence for >40m remains unavailable in the material provided; soil C is a provisional selection, not a site-classification acceptance.

## Stage 02 slab load path study and area integration

Area Integration GUI: from ETABS 4-node area topology and assignment audit, prepare optional source-to-`ShellMITC4` *floor* and `E_SFI_MVLEM_3D` *wall* calls. **Use only if these elements do not already exist in the assembled model.** It does not assign loads or mass, perform gravity analysis, or validate FSAM. Its Excel/JSON inventory is a source topology audit only. Full use note: [Stage 02 review](../REVIEW_MAIN/00_MODEL/20261113_STAGE02_AREA_INTEGRATION_AND_SLAB_MESH_STUDY.md).

Meshes N=4, 8, 16 are subdivisions per source slab panel direction, not millimetres of element size. Prepare independent model configs; each requires an independently built and solved model. Current nomenclature is `MESH_04`, `MESH_08`, `MESH_16`; workbook `Slab_Load_Path_MESH_NN_V141.xlsx`. Never represent spreadsheet formula output alone as a solved force-response comparison.

For each mesh compare identical gravity source and support conditions, total applied kN and reaction kN, story vertical load, nodal shell-to-beam load transfer, beam end shear/moment, column/shear-wall vertical reaction, slab UZ, internal energy, and computation cost. Report percentage differences for 4→8 and 8→16. Mesh study cannot by itself close beam-column joint volume/offset or 32/76/97 support mismatches.

## Runtime problems and state interpretation (based on supplied November 12/13 logs)

The prior Kobe paired linear histories took **8040.21 s (XY)** and **8323.84 s (YX)**, 4094 accepted steps each. Model+gravity 95–97 s, damping/eigen 26 s, transient+recording 7917–8198 s, recording itself 245–253 s. This means ~98.5% of time was in transient+recording: a GUI redesign cannot make the native solve proportionally faster. Instrument solver setup, factorization, transient analyze() steps, element recorder calls, disk flush/CSV write and redraw timing. Profile baseline on fixed mesh and hardware. Do not weaken code time-step bounds or replace full record with an exploratory 0.1s diagnostic.

The clear-beam re-export's `Row number supplied was 1048577` is an Excel reader defect that was separately addressed with a bounded, gap-aware ETABS native workbook iterator. That correction is not proof that the ~320019.76 kN gravity profile matches source ETABS. All 32/76/97 support result comparisons remain independent.

**GUI rule:** label `NOT STARTED`, `RUNNING`, `COMPLETED`, `CANCELLED`, `FAILED`, `REVIEW REQUIRED` using unique statuses, progress from accepted steps, separate stop/terminate controls, and a persistent run manifest. A completed input conversion or workbook export must not imply a solver result is completed.

## Knowledge-base / reference policy

Every manuscript and model-setting claim should include a source register entry: title, authors/issuing body, publication year/date, version, journal/publisher, DOI where applicable, stable URL, clause/page and retrieval date, license/PDF location if openly available, and verified project applicability. A document being *cited* or *highly cited* is not validation of the model. See `LITERATURE/MASTER_LITERATURE_INDEX.csv` and topic folders for FVD, BRB, walls, concrete, steel and methods. PDF rights and source integrity must be respected.

### Known unresolved project decisions

1. Calibrated project M45, Fe500/Fe550 material and actual reinforcement, nonlinear wall FSAM, FVD and BRB device implementation.
2. Explicit vertical gravity and seismic mass provenance; beam-column/shear-wall joint and offset single ownership; independent ETABS 32/76/97 reaction comparison.
3. Actual adopted elastic stiffness, frame/shell properties, modal and P-Delta convergence checks and long-record XY/YX runs.
4. Native case/solver mapping and source identity hashes; no EDB mutation, and separate exploratory versus thesis-qualified results.
