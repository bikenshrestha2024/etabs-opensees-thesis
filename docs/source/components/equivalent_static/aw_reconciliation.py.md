# NBC Aw original Excel versus continuous-pier audit

Source: [aw_reconciliation.py](../../../../components/equivalent_static/aw_reconciliation.py)

Produces side-by-side original Excel/ETABS-linked wall-index and OpenSees gross/continuous-pier diagnostic values for both axes, requiring the exact original ETABS EDB identity or byte-identical source hash. Independently checks that source spreadsheet row contributions sum to workbook Aw. It never writes to the original EDB, original Excel calculator, or engine.

Output: `Aw_Reconciliation/NBC105_Aw_Reconciliation.json` and `.xlsx`. Different wall segment definitions remain unpaired unless common wall-object IDs are verified. Gross projected wall indices and continuous-through-height metrics do not automatically satisfy NBC 105:2025 §5.1.2. See `docs/00_THESIS_ACCEPTANCE_GATES.md` for required source verification.
