# ETABS native material/section/frame assignment crosswalk

**Canonical source:** [`components/validation/etabs_assignment_gravity_audit.py`](../../../../components/validation/etabs_assignment_gravity_audit.py)

## Function and evidence boundary

Read-only full native ETABS assignment XLSX extraction; checks Material List by Object Type, Section Prop, frame UniqueName, frame end offsets, insertion points and self-weight pattern. Compares original beam IDs, lengths, offsets and summed native beam weight with OpenSees source candidate. Rejects mismatched native totals before allowing source correction. Original workbook remains unchanged.

## Engineering acceptance

Source-file syntax and synthetic Python unit tests are separate from project-level ETABS↔OpenSees equivalence. Verification of the original EDB/Excel SHA, native 32-node support reactions, EQX/EQY/PDelta results, OpenSees solver convergence, and NBC 105:2025 acceptance remains **NOT VERIFIED** until original project evidence is generated and reviewed. Keep current filename schema and source code intact unless a complete tested migration is approved.

## Developer discipline

Read [canonical engineering rules](../../../../engineering/rules/CORE_RULES.md), current entry points and related tests before editing. Do not duplicate existing implementation, silently change physical loads or modify the original EDB. Record detailed run logs, source table names, units and files in one evidence folder. This guide documents current intended responsibility; it does **not** certify every branch or native case has been inspected.
