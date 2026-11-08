"""Centralized review-evidence paths for the gravity GUI.

This module packages already-generated evidence only. It does not run ETABS
or OpenSees and does not infer model equivalence from force equilibrium.
[REF docs/source/components/gravity/comparison_bundle.py.md]
"""
from __future__ import annotations
from pathlib import Path
from components.gravity.comparison_bundle import export_bundle


def latest_dual_run(gravity_root):
    """Find the most recent two-case result without substituting absent data.

    [REF components/gravity/support_scenarios.py]
    """
    base=Path(gravity_root)/"Gravity_Wall_Base_Comparison"
    if not base.is_dir():
        return None
    matches=sorted((p for p in base.iterdir()
        if p.is_dir()
        and (p/"ETABS_SOURCE_SUPPORTS"/"Gravity_Result_V110.json").is_file()
        and (p/"CONTINUOUS_WALL_BASE_FIXED"/"Gravity_Result_V110.json").is_file()),
        reverse=True)
    return matches[0] if matches else None


def package_gravity_review(model_script, gravity_root, *,
                           single_run=None, dual_run=None, etabs_json=None,
                           max_file_mb=40):
    """Gather files and create a versioned ZIP under one central upload folder.

    [REF components/gravity/comparison_bundle.py export_bundle]
    """
    model=Path(model_script).expanduser().resolve()
    root=Path(gravity_root).expanduser().resolve()
    if not model.is_file():
        raise FileNotFoundError("Generated gravity model script missing: "+str(model))
    dual=Path(dual_run).resolve() if dual_run is not None else latest_dual_run(root)
    gravity=(Path(single_run).resolve() if single_run is not None else
             dual/"ETABS_SOURCE_SUPPORTS" if dual else root)
    result=gravity/"Gravity_Result_V110.json"
    if not result.is_file():
        raise FileNotFoundError("Required OpenSees gravity result missing: "+str(result))
    output=root/"Gravity_Evidence_Upload"
    source_etabs=None
    if etabs_json:
        path=Path(etabs_json).expanduser().resolve()
        if path.is_file():
            source_etabs=path
    report,zip_path=export_bundle(
        model.parent,gravity,output,
        etabs_json=source_etabs,
        dual_run_dir=dual,
        comparison_root=root,
        max_file_mb=max_file_mb)
    folder=Path(report["output_folder"])
    paths={
        "source_export":str(model.parent),
        "gravity_root":str(root),
        "selected_gravity_run":str(gravity),
        "selected_dual_run":str(dual) if dual else None,
        "upload_folder":str(output),
        "upload_zip":str(zip_path),
        "extracted_evidence_folder":str(folder),
        "evidence_manifest":str(folder/"EVIDENCE_MANIFEST.json"),
        "exact_file_paths":str(folder/"EVIDENCE_FILE_PATHS.txt"),
        "gui_action_log":str(root/"Gravity_GUI_Actions.log"),
        "missing_file_count":len(report["missing"]),
        "oversized_file_count":len(report["oversize_skipped"]),
        "engineering_acceptance":"NOT_ESTABLISHED_BY_PACKAGING"
    }
    return report,paths


def path_log_entries(paths,report):
    """Provide deterministic full paths and warnings for the GUI and logfile.

    [REF docs/source/components/gravity/comparison_bundle.py.md]
    """
    entries=[]
    for key,value in paths.items():
        if value is not None:
            entries.append(("EVIDENCE_"+key.upper(),str(value)))
    for item in report["missing"]:
        entries.append(("EVIDENCE_MISSING",str(item)))
    for item in report["oversize_skipped"]:
        entries.append(("EVIDENCE_OVERSIZE",str(item)))
    entries.append(("EVIDENCE_STATUS",
        "Upload ZIP ready; inspect manifest. Packaging does not establish "
        "ETABS/OpenSees engineering equivalence."))
    return entries
