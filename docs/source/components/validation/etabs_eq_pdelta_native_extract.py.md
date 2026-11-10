# Native ETABS EQX/EQY and PDelta table extraction

**Canonical source:** [`components/validation/etabs_eq_pdelta_native_extract.py`](../../../../components/validation/etabs_eq_pdelta_native_extract.py)

## Function and evidence boundary

Queries already saved native ETABS cases, step-qualified reactions and table headers. Saves case-aware evidence without modifying EDB or initiating design. Synthetic tests must provide a SapModel.LoadCases mock when the extractor accesses that object. ETABS v23 native API output must be validated, not assumed.

## Engineering acceptance

Source-file syntax and synthetic Python unit tests are separate from project-level ETABS↔OpenSees equivalence. Verification of the original EDB/Excel SHA, native 32-node support reactions, EQX/EQY/PDelta results, OpenSees solver convergence, and NBC 105:2025 acceptance remains **NOT VERIFIED** until original project evidence is generated and reviewed. Keep current filename schema and source code intact unless a complete tested migration is approved.

## Developer discipline

Read [canonical engineering rules](../../../../engineering/rules/CORE_RULES.md), current entry points and related tests before editing. Do not duplicate existing implementation, silently change physical loads or modify the original EDB. Record detailed run logs, source table names, units and files in one evidence folder. This guide documents current intended responsibility; it does **not** certify every branch or native case has been inspected.
