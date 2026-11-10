# Gravity RCC overlap and beam-source scenario reconciliation

**Canonical source:** [`components/gravity/joint_weight_reconciliation.py`](../../../../components/gravity/joint_weight_reconciliation.py)

## Function and evidence boundary

Produces per-source ETABS object quantities and mutually exclusive gravity scenarios. Never applies potential beam-offset deduction together with separate RCC overlap correction. Requires consistent per-beam gross weights and source ledgers. Earlier results require a native 32-support rerun; no automatic acceptance is claimed.

## Engineering acceptance

Source-file syntax and synthetic Python unit tests are separate from project-level ETABS↔OpenSees equivalence. Verification of the original EDB/Excel SHA, native 32-node support reactions, EQX/EQY/PDelta results, OpenSees solver convergence, and NBC 105:2025 acceptance remains **NOT VERIFIED** until original project evidence is generated and reviewed. Keep current filename schema and source code intact unless a complete tested migration is approved.

## Developer discipline

Read [canonical engineering rules](../../../../engineering/rules/CORE_RULES.md), current entry points and related tests before editing. Do not duplicate existing implementation, silently change physical loads or modify the original EDB. Record detailed run logs, source table names, units and files in one evidence folder. This guide documents current intended responsibility; it does **not** certify every branch or native case has been inspected.
