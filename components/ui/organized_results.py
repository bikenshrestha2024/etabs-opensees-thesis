"""Non-destructive per-module result snapshot and review ZIP publisher.

[REF docs/source/components/ui/organized_results.py.md]
Does not move active solver results: legacy paths, case registries and historical
reports remain readable. Snapshot copies are organized under one dated root.
The package is evidence for debugging, not structural-design certification.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

MODULES = ("Model", "Gravity", "ESM", "Modal", "MRSM", "LinearTH", "NonlinearTH", "Comparisons", "Unclassified")
SKIP_DIRS = {
    "Organized_Results", "REVIEW_SNAPSHOTS", "Seismic_Review_Packages", "Gravity_Evidence_Upload",
    "__pycache__", ".git", ".pytest_cache",
}
SKIP_EXT = {".edb", ".bak", ".lock", ".tmp", ".pyc"}
SKIP_SUFFIXES = (".processing.json", ".processing.log", ".tmp")
METHOD_MARKERS = {
    "Model": ("mesh_04", "mesh_08", "mesh_16", "element_connectivity", "model_config"),
    "Gravity": ("gravity", "joint_weight", "load_path", "support_reaction",
                "slab_self_weight", "clear_beam", "foundation_reaction"),
    "ESM": ("esm", "equivalent_static", "nbc105", "rayleigh_preliminary",
            "input_sync", "aw_reconciliation", "etabs_linked"),
    "Modal": ("modal", "eigen", "mass_participation"),
    "MRSM": ("mrsm", "response_spectrum", "cqc", "spectrum"),
    "LinearTH": ("linear_time_history", "linear_th", "ltha", "lth_"),
    "NonlinearTH": ("nonlinear_time_history", "nonlinear_th", "nltha", "nth_"),
    "Comparisons": ("etabs_comparison", "etabs_opensees_equivalence",
                    "case_comparison", "equivalence", "comparison"),
}


def sha256(path):
    """[REF docs/source/components/ui/organized_results.py.md] Hash saved evidence exactly."""
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def classify(path, relative=None):
    """[REF docs/source/components/ui/organized_results.py.md] Classify stored outputs, not science."""
    p = Path(relative or path)
    parts = [part.casefold() for part in p.parts]
    name = p.name.casefold()
    # First classify explicit full stage names, never guess an NLTHA result
    # from the shorter "ltha" substring. Historical aliases remain readable.
    if "02_model" in parts:
        return "Model"
    if any(x in ("07_nonlinear_time_history", "07_nonlinear_th") for x in parts):
        return "NonlinearTH"
    if any(x in ("06_linear_time_history", "06_linear_th") for x in parts):
        return "LinearTH"
    # Folder membership overrides filename where possible; this keeps an
    # ETABS comparison within its own Comparison folder, not the ESM bundle.
    if any(x.startswith(("etabs_comparison", "gravity_case_comparison",
                         "gravity_wall_base_comparison")) for x in parts[:-1]):
        return "Comparisons"
    # Nested modal caches within MRSM case folders remain modal evidence.
    if any(x.startswith(("modal_", "modal-")) for x in parts[:-1]):
        return "Modal"
    if any(x.startswith(("mrsm_", "mrsm-")) for x in parts[:-1]):
        return "MRSM"
    if any(x.startswith(("gravity_", "gravity-")) for x in parts[:-1]):
        return "Gravity"
    if any(x.startswith(("etabs_linked_esm", "aw_reconciliation", "nbc105_input_sync"))
           for x in parts[:-1]):
        return "ESM"
    # Comparison needs priority for explicitly labelled evidence files.
    if any(x in name for x in METHOD_MARKERS["Comparisons"]):
        return "Comparisons"
    for module in ("NonlinearTH", "LinearTH", "MRSM", "Modal", "Gravity", "ESM", "Model"):
        if any(x in name for x in METHOD_MARKERS[module]):
            return module
    return "Unclassified"


def _walk(root, *, destination):
    root = Path(root).resolve()
    destination = Path(destination).resolve()
    for parent, dirs, names in os.walk(root, followlinks=False):
        here = Path(parent)
        dirs[:] = sorted(d for d in dirs
                         if d not in SKIP_DIRS and
                         not (here / d).is_symlink() and
                         (here / d).resolve() != destination and
                         destination not in (here / d).resolve().parents)
        for name in sorted(names):
            path = here / name
            if path.is_symlink() or not path.is_file():
                continue
            if path.suffix.casefold() in SKIP_EXT or name.casefold().endswith(SKIP_SUFFIXES):
                continue
            # Avoid recursively packaging ZIPs and old generated archives.
            if path.suffix.casefold() == ".zip":
                continue
            yield path, path.relative_to(root)


def publish_organized_results(results_root, *, gravity_root=None,
                              include_unclassified=True, destination_parent=None,
                              selected_modules=None, bundle_name="ALL_MODULES"):
    """[REF docs/source/components/ui/organized_results.py.md] Create dated folder and ZIPs.

    results_root is the existing source/model/state output folder (e.g. ULS...).
    An optional gravity_root includes the independently selected gravity GUI
    output if it lives elsewhere. Do not recurse through earlier snapshots.
    """
    root = Path(results_root).expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError("Selected analysis result directory does not exist: " + str(root))
    allowed = frozenset(selected_modules) if selected_modules is not None else None
    if allowed is not None and (not allowed or not allowed.issubset(MODULES)):
        raise ValueError("Unknown or empty selected modules")
    roots = [("Analysis", root)]
    if gravity_root:
        grav = Path(gravity_root).expanduser().resolve()
        if not grav.is_dir():
            raise FileNotFoundError("Selected gravity output root missing: " + str(grav))
        if grav != root:
            roots.append(("GravityGUI", grav))
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    parent = Path(destination_parent).expanduser().resolve() if destination_parent else root / "Organized_Results"
    if parent == root:
        raise ValueError("Destination parent may not be the source results root")
    destination = parent / stamp
    destination.mkdir(parents=True, exist_ok=False)
    manifest = {
        "schema": "thesis-module-evidence-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "original_results_root": str(root),
        "gravity_output_root": str(roots[1][1]) if len(roots) > 1 else None,
        "status": "OUTPUT_INDEX_NOT_ENGINEERING_ACCEPTANCE",
        "entries": [], "skipped": [], "modules": {}, "source_sha256": {},
    }
    # First enumerate evidence and hash all source files, then copy. Never
    # use fuzzy model-state matching or edit active result files.
    listed = []
    for source_label, source_root in roots:
        for path, rel in _walk(source_root, destination=destination):
            module = classify(path, rel)
            if source_label == "GravityGUI" and module == "Unclassified":
                module = "Gravity"
            if allowed is not None and module not in allowed:
                manifest["skipped"].append({"source": str(path), "reason": "MODULE_NOT_SELECTED", "module": module})
                continue
            if module == "Unclassified" and not include_unclassified:
                manifest["skipped"].append({
                    "source": str(path), "reason": "UNCLASSIFIED_NOT_INCLUDED"})
                continue
            listed.append((source_label, source_root, path, rel, module))
    if not listed:
        raise ValueError("No classifiable saved results. No ZIPs generated; check module output roots.")
    for source_label, source_root, original, rel, module in listed:
        dest = destination / module / source_label / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original, dest)
        digest = sha256(original)
        if sha256(dest) != digest:
            raise IOError("Postcopy SHA256 mismatch: " + str(original))
        manifest["entries"].append({
            "module": module, "source": str(original),
            "snapshot": dest.relative_to(destination).as_posix(),
            "bytes": original.stat().st_size, "sha256": digest,
            "source_root": str(source_root),
        })
    # A single exact manifest makes it possible to review or regenerate the
    # evidence without assuming analysis results are from the same EDB.
    counts = {module: sum(x["module"] == module for x in manifest["entries"])
              for module in MODULES}
    manifest["modules"] = counts
    manifest["file_count"] = len(manifest["entries"])
    manifest_file = destination / "EVIDENCE_MANIFEST.json"
    manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    readme = destination / "README_FIRST.txt"
    readme.write_text(
        "THESIS ANALYSIS OUTPUT SNAPSHOT\n"
        "Folders: Model, Gravity, ESM, Modal, MRSM, LinearTH, NonlinearTH, Comparisons, Unclassified.\n"
        "Original solver output files are UNCHANGED. These are verified copies.\n"
        "Cases are grouped by original relative path; no cross-source equivalence is inferred.\n"
        "Missing SLS/native ETABS output stays missing, not zero.\n"
        "Review EVIDENCE_MANIFEST.json for source path and SHA256 of every copy.\n"
        "The ZIPs are meant for sharing and debugging. They do not establish code compliance.\n",
        encoding="utf-8")
    zipdir = destination / "ZIP_Exports"
    zipdir.mkdir()
    archives = {}
    def archive(name, entries):
        target = zipdir / (name + "_Review_UPLOAD.zip")
        with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED,
                             compresslevel=6, allowZip64=True) as z:
            z.write(manifest_file, "EVIDENCE_MANIFEST.json")
            z.write(readme, "README_FIRST.txt")
            for entry in entries:
                path = destination / entry["snapshot"]
                z.write(path, entry["snapshot"])
        archives[name] = str(target)
    for module in MODULES:
        subset = [e for e in manifest["entries"] if e["module"] == module]
        if subset:
            archive(module, subset)
    if not bundle_name or "/" in bundle_name or "\\" in bundle_name:
        raise ValueError("Invalid archive bundle name")
    archive(bundle_name, manifest["entries"])
    latest = parent / "LATEST_ORGANIZED_RESULT.txt"
    latest.write_text(
        "FOLDER: " + str(destination) + "\n"
        "MANIFEST: " + str(manifest_file) + "\n" +
        "".join(label + "_ZIP: " + path + "\n" for label, path in archives.items()),
        encoding="utf-8")
    return {
        "folder": str(destination), "manifest": str(manifest_file),
        "zip_files": archives, "file_count": len(manifest["entries"]),
        "module_counts": counts, "skipped_count": len(manifest["skipped"]),
        "status": manifest["status"],
    }
