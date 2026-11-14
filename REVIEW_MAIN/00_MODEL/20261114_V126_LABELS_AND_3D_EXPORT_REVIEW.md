# V126 source-property GUI — canonical display aliases and 3D figure export

## Observed bug / native input evidence
User's Windows V126 screenshot shows source objects `FRAME1 / Storey 11`, `FRAME2 / Storey 20`, numeric topology `11001`, `20001`, solver tags `100001`, `100002`, instead of human source labels `C1101`, `C2009`. Independent `OpenSees_ID_Lookup(1).html` already has a `Display label (not solver tag)` column (e.g. `C1101`). The V126 Matplotlib pane has toolbar save controls but lacks an explicitly named 3D export button. The source `components/sections/mapping_gui.py` populated the tree from `collect()` without requesting the shared label builder.

## Changes
- `components/sections/mapping_audit.py::collect` uses the identical `components.model.display_ids.build_labels` method and identical native identity `dimension:etabs_object` used by `components/model/id_audit.py`. This creates consistent user-facing labels `B/C/BR/CO/BT/CT/SW/FL`, strictly according to the existing **ETABS source category**, story and deterministic position within each category/story. No geometric inference of outrigger classification.
- V126 parent, child and topology table cells now display the alias alongside original source object and numeric topology tag. Tooltips and highlighted selection annotation show the alias where available. ETABS IDs, topology numbers, actual OpenSees solver tags, recorder IDs, node tags and config keys are never renamed.
- Explicit **Export 3D figure…** button saves displayed Matplotlib view/selection as PNG (240 DPI), SVG or PDF with user-chosen location and error reporting. It does not rerun a solver, alter project geometry or claim source/load validation.
- Existing `Export / open Excel audit` remains available; because `collect` now includes `display_label`, the next workbook export also includes the source display alias.

## Scope and limitations
- `UNCLASSIFIED_MEMBER` remains intentional if ETABS source category or storey is unavailable; no invented C/BT/CT labels.
- `C1101` is **not** the integer OpenSees solver tag. Native tag stays `100001` in the screenshot's first frame example. The category labels are aliases only.
- The on-screen figure export button is for the V126 embedded Matplotlib **3D source geometry**. HTML/Plotly views retain their separate controls and need their own UI change if a different “figure 3” was intended.
- The source EDB and all analysis outputs remain read-only/unchanged. For the submitted PDF/ZIP/XLSX files, private provenance and engineering validation are separate.

## Acceptance
1. Run V126 with same exported model; first row should display `C1101 / FRAME:1 / Storey 11`, and topology cell `C1101 (11001)`, retaining solver `100001`.
2. Check category filters for beams, columns, floors, walls and a **source-classified** CO/BT/CT; no auto-classification from section shape.
3. Select an element, verify the magenta highlight and alias annotation; export PNG, SVG and PDF and inspect current orientation and highlight.
4. Export Excel and confirm `Elements and mappings` contains `display_label` values.
5. Confirm no numerical tags or OpenSees connectivity changed via source-model checksum and existing comparison tests.

**Evidence state:** code updated and static tests wired; Windows Tk GUI export and native model acceptance still pending. Do not claim a screenshot test occurred in GitHub CI.
