# NBC Aw comparison — selected 12m walls, old Excel and original OpenSees pier diagnostic

Source: [aw_reconciliation.py](../../../../components/equivalent_static/aw_reconciliation.py)

**2026-11-12 policy:** the user selected two continuous X wall lines, each 12m long with two 2m first-storey circulation doors. The exported shell/node data confirms their planes, spans, two simultaneous openings, thickness and upper closure. Under NBC 105:2025 §5.1.2 (UBC 1997 and SEAOC 1997 UBC historical whole-wall interpretive precedent), selected AwX=**2.073174515 m²** and AwY=**2.203080332 m²** when the current source export passes the project-specific node/shell checks.

The original 6m-panel Excel value **1.958293629 m²** and the original OpenSees full-storey continuous-pier X **1.930637119 m²** are deliberately preserved as historical / sensitivity diagnostics. **Never** use `snapshot['aw_candidate_m2']` as the continuous-pier diagnostic after the 12m policy has been adopted. Read `snapshot['continuous_pier_diagnostic']['aw_candidate_m2']` explicitly; the reconciliation exporter now does this.

This function is a strict **same-EDB original Excel provenance** comparison. It requires a matching original ETABS EDB identity and original workbook audit, verifies the sum of actual Excel row contributions, and exports separate columns for selected 12m Aw, historical Excel Aw, continuous-pier Aw, gross projection, their differences, and code review statuses. No underlying data/model/Excel is changed; failed source-identity gate is not bypassed for a prettier plot.

The discrepancy is caused by using different wall lengths in the empirical `(Lwi/H)^2` term. Original OpenSees pier method independently weights 2m, 4m, 2m segments in each wall plane; old Excel treats each architectural 6m bay as a wall; the selected method correctly groups each connected 12m perforated wall. For the node source inspection and source authors/DOIs, see [completed review](../../../../REVIEW_MAIN/02_ESM/Aw_Validation/20261112_EXPORT_NODE_GEOMETRY_REVIEW_COMPLETED.md).

Output: `Aw_Reconciliation/NBC105_Aw_Reconciliation.json` and `.xlsx`. Source IDs and wall intersections still require independent native ETABS OAPI response and coupling verification; `GEOMETRY_REVIEW_COMPLETED` is not `CODE_ACCEPTED`.
