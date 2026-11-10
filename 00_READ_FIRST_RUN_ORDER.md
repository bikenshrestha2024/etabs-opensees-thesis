# Start here - ETABS to OpenSeesPy research workflow

Run **`01.py`** from the complete checkout for the main GUI.
For individual tools, use the [current launcher index](docs/programs/00_PROGRAM_INDEX.md).
Keep the package intact, including `components/`, runtime facades and source guides.

The [engineering dependency map](docs/review/00_CANONICAL_RUN_ORDER_AND_NAMING.md)
explains the evidence needed at each stage. Launcher numbers are navigation IDs,
not a mandatory run-all sequence. Linear time history is a useful cross-check;
it is not a prerequisite analysis whose results must be loaded before NLTHA.

1. Establish source/model identity and review inputs (`01`, `02`, `22`).
2. Configure and benchmark sections, materials and devices (`03`-`09`, `29`, `30`).
3. Verify gravity load paths, restraints and P-Delta basis (`10`, `19`, `20`).
   For an unfactored gravity comparison use **1.0D + 1.0L**, including assigned
   roof live. Seismic preload and seismic mass factors have separate purposes;
   inspect the actual configuration, occupancy and applicable NBC provisions.
4. Review modal/damping evidence and linear cross-checks (`11`-`14`, `32`-`35`).
5. Diagnose isolated nonlinear cases before full paired histories (`15`-`17`, `21`).
6. Interpret only completed, qualified cases (`18`, `27`, `36`, `37`).
   The matrix generator plans cases; the dashboard reports evidence presence.
   Neither executes or certifies a full earthquake suite.

**Open engineering work:** the documented full-building first-step nonlinear
failure and project material/reinforcement qualification require native evidence.
This software/navigation review does not establish a validated optimum outrigger
position or NBC compliance.

[First Windows test](docs/00_TEST_MAIN_AFTER_MERGE.md) ·
[Historical rename map](docs/00_WORK_ORDER_RENAME_MAP.md) ·
[Review ledger](docs/review/ledger/README.md)

[Clean numbered launcher list](launchers/README.md) · [All Excel workbooks](excel/README.md)
