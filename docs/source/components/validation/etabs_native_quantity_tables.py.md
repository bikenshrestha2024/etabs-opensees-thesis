# ETABS native quantity table parser

**Canonical source:** [`components/validation/etabs_native_quantity_tables.py`](../../../../components/validation/etabs_native_quantity_tables.py)

## Function and evidence boundary

Reads native CSI ETABS DatabaseTables/material quantity data with explicit case, table/header and return-code validation. ETABS v23 six-field GetTableForDisplayArray wrapper is supported by source-specific tests. Quantity proof does not on its own resolve material self-weight and 32-support reaction discrepancies.

## Engineering acceptance

Source-file syntax and synthetic Python unit tests are separate from project-level ETABS↔OpenSees equivalence. Verification of the original EDB/Excel SHA, native 32-node support reactions, EQX/EQY/PDelta results, OpenSees solver convergence, and NBC 105:2025 acceptance remains **NOT VERIFIED** until original project evidence is generated and reviewed. Keep current filename schema and source code intact unless a complete tested migration is approved.

## Developer discipline

Read [canonical engineering rules](../../../../engineering/rules/CORE_RULES.md), current entry points and related tests before editing. Do not duplicate existing implementation, silently change physical loads or modify the original EDB. Record detailed run logs, source table names, units and files in one evidence folder. This guide documents current intended responsibility; it does **not** certify every branch or native case has been inspected.
