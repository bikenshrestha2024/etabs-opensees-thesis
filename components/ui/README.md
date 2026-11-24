# Desktop application and results navigation

**Active owner:** `components/ui/` · **Current Python modules:** 20 · **Status:** module navigation only; engineering acceptance requires independent evidence.

## Responsibilities and interfaces

**Inputs and authority:** Published model/source/run manifests and module APIs; never invent or approve numerical data.

**Cross-module contracts:** Visible workflows, status, selection filters and saved-case plots/reports.

**Output ownership:** GUI is a presentation layer; each producer retains its own stage output.

All modules follow [the active integration and latest-source policy](../../docs/architecture/ACTIVE_MODULE_INTEGRATION_AUDIT_20261122.md) and [the uniform output structure](../../docs/architecture/UNIFORM_OUTPUT_STRUCTURE_20261122.md). Source EDB and workbook identity require actual SHA-256 verification; source file names, modification times and passing syntax tests never establish structural equivalence. Historical V134 module indexes are compatibility history, not an authoritative current file inventory.

## Current Python source files

- [application.py](application.py)
- [assembled_mesh_view.py](assembled_mesh_view.py)
- [building_exploratory_gui.py](building_exploratory_gui.py)
- [case_selection.py](case_selection.py)
- [exploratory_options.py](exploratory_options.py)
- [history_inspection.py](history_inspection.py)
- [history_results.py](history_results.py)
- [history_review_tools.py](history_review_tools.py)
- [literature_demo_gui.py](literature_demo_gui.py)
- [nbc105_settings_panel.py](nbc105_settings_panel.py)
- [nltha_batch_gui.py](nltha_batch_gui.py)
- [organized_results.py](organized_results.py)
- [output_folder.py](output_folder.py)
- [plot_utilities.py](plot_utilities.py)
- [reference_documents.py](reference_documents.py)
- [response_viewer.py](response_viewer.py)
- [results.py](results.py)
- [saved_view_refresh.py](saved_view_refresh.py)
- [source_view_compaction.py](source_view_compaction.py)
- [view_controls.py](view_controls.py)
- [window_manager.py](window_manager.py)

> This list reflects the current checked-in Python files. Do not delete, rename or relocate an active module until its importers, GUI callbacks, saved-case readers and native regression evidence have been verified together. Source-specific guides are under `docs/source/components/ui/` where available.
