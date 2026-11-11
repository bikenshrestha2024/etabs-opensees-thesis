# All-storey NBC Rayleigh numerical audit

Source: [rayleigh_ledger_audit.py](../../../../components/modal/rayleigh_ledger_audit.py)

Pure helper verifying that the submitted seismic-weight ledger exactly covers the exported model diaphragm inventory, without duplicate master-node tags. Reconstructs NBC 105:2025 §5.1.1 Rayleigh period from verified `Wi`, `Fi`, and incremental elastic displacement `di` for each level: `2*pi*sqrt(sum(Wi*di**2)/(g*sum(Fi*di)))`.

This is a numerical reconstruction, not proof that an ETABS-extracted storey without a diaphragm has been included, or that the selected seismic weights, centre-of-mass displacements, torsion restraint or stiffness are NBC accepted.

Tests: `tests/test_rayleigh_ledger_audit.py`.
