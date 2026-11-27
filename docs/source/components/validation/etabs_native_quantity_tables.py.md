# ETABS native quantity table parser

**Canonical source:** [`components/validation/etabs_native_quantity_tables.py`](../../../../components/validation/etabs_native_quantity_tables.py)

## Function and evidence boundary

Reads native CSI ETABS DatabaseTables/material quantity data with explicit case, table/header and return-code validation. ETABS v23 six-field GetTableForDisplayArray wrapper is supported by source-specific tests. Quantity proof does not on its own resolve material self-weight and 32-support reaction discrepancies.

## Engineering acceptance

Source-file syntax and synthetic Python unit tests are separate from project-level ETABS↔OpenSees equivalence. Verification of the original EDB/Excel SHA, native 32-node support reactions, EQX/EQY/PDelta results, OpenSees solver convergence, and NBC 105:2025 acceptance remains **NOT VERIFIED** until original project evidence is generated and reviewed. Keep current filename schema and source code intact unless a complete tested migration is approved.

## Developer discipline

Read [canonical engineering rules](../../../../engineering/rules/CORE_RULES.md), current entry points and related tests before editing. Do not duplicate existing implementation, silently change physical loads or modify the original EDB. Record detailed run logs, source table names, units and files in one evidence folder. This guide documents current intended responsibility; it does **not** certify every branch or native case has been inspected.

## 2026-11-27 — gravity physical-equivalence evidence discovery

The direct gravity caller supplies its exact validated combination to the native database-table exporter. The exporter snapshots the separate DatabaseTables selection, clears cases, selects the requested combination, verifies readback and restores the original selection even if extraction fails. Missing selection APIs block scoped table collection rather than falsely claiming a matching result case. Catalog discovery now includes candidate families for all eight physical issues, including analytical connectivity, auto mesh, joint/edge constraints, section cuts and element joint forces. The manifest distinguishes no candidate, empty/failed candidate and nonempty raw candidate; no status certifies engineering equivalence. The existing evidence ZIP includes these files. Native table fields, case/step, units, topology, section-cut geometry and forces still need independent review. No source loads, stiffness or supports changed. Tests use synthetic CSI APIs; current EDB/workbook fingerprints unavailable.
