# Thesis decision register — 6 November 2026: original Excel NBC 105 method

## Current decision and explanation to retain

The user requests **the original ETABS-integrated Excel calculation method as the active ESM working reference for now**, with actual values read directly from its source `SCALING SUMMARY` sheet; OpenSees first-storey geometric intersection and read-only ETABS pier/void comparisons remain separate cross-checks. Treat the wall **above** an opening as a spandrel/coupling region in the physical OpenSees/ETABS structural model; do **not** append it automatically as an independent third first-storey wall term. Wall piers on either side of an opening may be separately identified for an independent-pier geometric approximation, but a perforated coupled wall may require different physical grouping. Neither NBC 105:2025 §5.1.2 nor the cited IITK-GSDMA commentary establishes a universal deduction of the vertical surface area of a door/window from `Aw`. Engineer review of pier/spandrel behavior is still needed for code acceptance.

The empirical wall index uses the official NBC expression:
```
Aw = sum_i Awi * [0.2 + (min(Lwi/H, 0.9))^2]
```
where `Awi` is first-storey effective **wall cross-sectional area** and `Lwi` is effective wall length along the horizontal earthquake action. See NBC 105:2025 §5.1.2 and IS 1893 (Part 1):2016 §7.6.2(b). IITGN-World Bank worked Example 8 and IITK-GSDMA commentary §C7.6.3 illustrate uninterrupted-wall applications; neither supplies a blanket opening reduction rule. Do not claim the coupled-wall interpretation is explicitly fixed by those examples.

## Implemented Excel-primary *reference* workflow

1. Open the real current ETABS/OpenSees **Ultimate→ULS** export; for Service use a separately matched Service→SLS export. Update local Git checkout from main.
2. In the ESM dialog choose **Use original Excel Aw/T (research)**. Select the actual completed `SCALING SUMMARY` `.xlsx` workbook. This button does **not** choose the other Excel template automatically, read stale hard-coded numbers, overwrite the workbook, call ETABS, or change OpenSees mesh/material/mass/gravity.
3. The parser extracts the actual **numeric** labelled X/Y wall indices (e.g. B16/B17 in a shifted workbook or B14/B15 for an earlier layout) and the corresponding optional workbook *NBC adopted period references*. It attaches exact workbook path, SHA256, real cell coordinates, original Source EDB and current export Source EDB. Invalid/missing values and opposite limit-state sources are rejected.
4. A workbook based on the original EDB when the current model is a differently hashed `- Copy.EDB` remains **DIFFERENT_EDB_RESEARCH_REFERENCE_ONLY**. With explicit user confirmation, the current ESM GUI can use its original values for an **exploratory apple-to-apple calculator-method comparison**. This is intentionally a separately selected exception to the automatic `source_workbooks()` eligibility gate, NOT a claim that the two source models have been validated equivalent.
5. If the workbook has a valid NBC adopted-period pair, the GUI explicitly enables workbook reference periods. These are **not ETABS eigenperiods** and **not OpenSees Rayleigh periods**. The legacy source-period option validates unchanged Aw and the NBC amplified-empirical bound. A changed area, mismatched state or bound failure blocks use. Rayleigh can be run later from the source model.
6. Calculated ESM outputs must retain `excel_method_direct_reference`, `diagnostic_only=true`, `wall_aw_code_accepted=false`, and `research_only_reason`. High-rise ULS ESM eligibility and all missing acceptance gates still require independent review. Do not relabel research comparisons as NBC design acceptance or claim verified ETABS↔OpenSees physical equivalence.

## Why not directly change the OpenSees effective area?

The original Excel values represent a particular original EDB and its specific wall classification, pier/spandrel grouping and opening treatment. A current `Copy` EDB may differ. Selecting the Excel approach makes the working calculator inputs traceable, but does not prove the current physical building has the same effective piers. Keep both separately labelled: **Excel original method**, **OpenSees actual mesh geometry**, and **ETABS read-only comparison**.

### Checklist for model equivalence

- Original and Copy EDB SHA256 identity, or independently reconciled beam/column/wall/pier geometry, openings, thickness, materials, mass, support constraints and model modifications.
- First-storey physical wall lengths and opening locations, plus whether wall above opening supplies coupling (retained in structural model but not auto-counted as a separate `Awi`).
- Separate directional OpenSees Rayleigh and ETABS modal periods, drift/mass and RSA comparisons; workbook NBC adopted period is not a substitute.
- Full modal/MRSM/NLTHA numerical and code acceptance gates as documented in the thesis repository.

**This file is the persistent repository decision record for later work.** The user may separately manage the ChatGPT Memory summary in Settings > Personalization; a Git commit does not modify ChatGPT account Memory.
