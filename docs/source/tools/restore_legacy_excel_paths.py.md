# restore_legacy_excel_paths.py

Read-only planning by default: `python tools/restore_legacy_excel_paths.py`.
Add `--restore` only when reproducing an old saved snapshot that expects
workbooks at their former paths. It verifies the catalogued SHA256, refuses
paths outside the checkout, and never overwrites a different existing file.
The resulting optional copies are local compatibility artifacts; committed
workbooks have their authoritative location under excel/.
