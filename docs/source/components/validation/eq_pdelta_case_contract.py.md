# ETABS EQX/EQY P-Delta case-contract definition

**Canonical source:** [`components/validation/eq_pdelta_case_contract.py`](../../../../components/validation/eq_pdelta_case_contract.py)

## Function and evidence boundary

Defines case-name matching, source selection and expected case evidence. Native ETABS tables may vary by CSI version, require validation of case/step/direction and source identity. Does not run ETABS or replace actual model results.

## Engineering acceptance

Source-file syntax and synthetic Python unit tests are separate from project-level ETABS↔OpenSees equivalence. Verification of the original EDB/Excel SHA, native 32-node support reactions, EQX/EQY/PDelta results, OpenSees solver convergence, and NBC 105:2025 acceptance remains **NOT VERIFIED** until original project evidence is generated and reviewed. Keep current filename schema and source code intact unless a complete tested migration is approved.

## Developer discipline

Read [canonical engineering rules](../../../../engineering/rules/CORE_RULES.md), current entry points and related tests before editing. Do not duplicate existing implementation, silently change physical loads or modify the original EDB. Record detailed run logs, source table names, units and files in one evidence folder. This guide documents current intended responsibility; it does **not** certify every branch or native case has been inspected.
