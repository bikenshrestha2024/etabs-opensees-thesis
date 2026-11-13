"""Independent, auditable ShellMITC4 4/8/16 mesh-case assembly (02 Model).

Each case is built from the identical saved ETABS *source audit*, never from
another mesh's assembled finite-element model. The source export remains
unchanged. No native ETABS or gravity solver is run by this helper.

REF docs/source/components/gravity/mesh_cases.py.md
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from uuid import uuid4
import json
import shutil

MESH_SIZES = (4, 8, 16)
REQUIRED_SOURCE = (
    "OpenSees_Element_Connectivity.json",
    "OpenSees_Section_Assignment_Audit.json",
    "OpenSees_Load_Conversion_Audit.json",
    "OpenSees_Complete_Model_Config_V118.json",
)
OPTIONAL_SOURCE = (
    "OpenSees_Area_Section_Assignment_Audit.json",
    "OpenSees_Source_Model_Metadata_V118.json",
    "ETABS_Materials.csv",
    "OpenSees_Section_Assignment_Audit.csv",
    "OpenSees_Area_Section_Assignment_Audit.csv",
    "ETABS_to_OpenSees_Element_Mapping.csv",
    "OpenSees_Source_Model_Metadata_V118.csv",
)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def case_base(folder, subdivisions):
    n = int(subdivisions)
    if n not in MESH_SIZES:
        raise ValueError("Mesh comparison supports only 4, 8 and 16 subdivisions")
    return Path(folder) / "02_MODEL" / "SLAB_LOAD_PATH" / f"MESH_{n:02d}"


def prepared_configs(folder):
    """Create three labeled *configurations*, not completed analysis cases."""
    folder = Path(folder).resolve()
    config_path = folder / REQUIRED_SOURCE[3]
    if not config_path.is_file():
        raise FileNotFoundError("Export the ETABS source model and config first.")
    cfg = json.loads(config_path.read_text(encoding="utf-8-sig"))
    target_dir = folder / "02_MODEL" / "SLAB_LOAD_PATH" / "PREPARED_CONFIGS"
    target_dir.mkdir(parents=True, exist_ok=True)
    result = []
    for n in MESH_SIZES:
        target = target_dir / f"Model_Config_MESH_{n:02d}.json"
        prepared = dict(cfg, floor_subdivisions=n)
        # No output implies an assembled/solved case. Replacements here are
        # config-only and checked again when copied to a unique run directory.
        target.write_text(json.dumps(prepared, indent=2, ensure_ascii=False), encoding="utf-8")
        result.append(target)
    return result


def stage_case(folder, subdivisions):
    """Copy source inputs into an isolated, unique case run; never mutate root."""
    folder = Path(folder).resolve()
    n = int(subdivisions)
    parent = case_base(folder, n) / "RUNS"
    missing = [f for f in REQUIRED_SOURCE if not (folder / f).is_file()]
    if missing:
        raise FileNotFoundError("This export has missing required ETABS audit inputs: " + ", ".join(missing))
    root_config = json.loads((folder / REQUIRED_SOURCE[3]).read_text(encoding="utf-8-sig"))
    prepared = folder / "02_MODEL" / "SLAB_LOAD_PATH" / "PREPARED_CONFIGS" / f"Model_Config_MESH_{n:02d}.json"
    if prepared.is_file():
        chosen = json.loads(prepared.read_text(encoding="utf-8-sig"))
        expected = dict(root_config, floor_subdivisions=n)
        if chosen != expected:
            raise ValueError(
                f"MESH_{n:02d} prepared configuration is stale relative to current project "
                "model settings. Re-run 'Prepare MESH_04/08/16 configurations' before assembling."
            )
    else:
        chosen = dict(root_config, floor_subdivisions=n)
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid4().hex[:8]
    run_dir = parent / f"RUN_{run_id}"
    run_dir.mkdir(parents=True, exist_ok=False)
    provenance = {}
    for filename in REQUIRED_SOURCE + OPTIONAL_SOURCE:
        source = folder / filename
        if source.is_file():
            target = run_dir / filename
            shutil.copy2(source, target)
            provenance[filename] = digest(target)
    config = run_dir / REQUIRED_SOURCE[3]
    config.write_text(json.dumps(chosen, indent=2, ensure_ascii=False), encoding="utf-8")
    provenance[config.name] = digest(config)
    manifest = {
        "status": "STAGED_NOT_ASSEMBLED",
        "mesh_subdivisions": n,
        "source_export": str(folder),
        "source_model_unchanged": True,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_file_sha256": provenance,
        "meaning": "ETABS saved source audit copied to mesh-specific folder; no solver executed",
    }
    (run_dir / "MESH_CASE_PROVENANCE.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return run_dir


def build_case(folder, subdivisions, *, runtime_dir=None):
    """Stage, assemble fresh mesh and export formula workbook for that mesh only.

    This is intentionally a potentially expensive operation and must run in a
    GUI worker thread. Other native solver stages, gravity and ETABS parity
    remain separate. On failure keep the case run + error JSON for diagnosis.
    """
    run_dir = stage_case(folder, subdivisions)
    n = int(subdivisions)
    log = run_dir / "MESH_BUILD_STATUS.json"
    def record(status, **extra):
        report = dict(mesh_subdivisions=n, status=status, run_directory=str(run_dir),
                      updated_utc=datetime.now(timezone.utc).isoformat(), **extra)
        log.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        return report
    record("ASSEMBLY_RUNNING")
    try:
        from OpenSees_Complete_Export_V118 import prepare_complete_export
        if runtime_dir is None:
            # This package may be loaded through legacy compatibility facades;
            # resolve runtime from the real source module rather than cwd.
            from components.model import assembly
            runtime_dir = Path(assembly.__file__).resolve().parents[2]
        manifest, report = prepare_complete_export(str(run_dir), runtime_dir=Path(runtime_dir))
        if report.get("assembly_errors") or not manifest.get("elastic_assembled"):
            raise RuntimeError("Mesh assembly blocked: " + "; ".join(report.get("assembly_errors", [])))
        # Verify that the model identity was derived from this run's saved cfg.
        model_path = run_dir / "OpenSees_Complete_Model_Data_V118.json"
        data = json.loads(model_path.read_text(encoding="utf-8-sig"))
        cfgpath = run_dir / REQUIRED_SOURCE[3]
        if data.get("config_sha256") != digest(cfgpath):
            raise RuntimeError("Mesh model/config SHA256 disagreement after assembly; no workbook exported.")
        cfg = json.loads(cfgpath.read_text(encoding="utf-8-sig"))
        if int(cfg.get("floor_subdivisions", -1)) != n:
            raise RuntimeError("Mesh size was not preserved by model assembly.")
        from OpenSees_Load_Path_V141 import export
        workbook = export(run_dir, output_root=case_base(folder, n))
        result = record(
            "FORMULA_WORKBOOK_CREATED_NOT_GRAVITY_VERIFIED",
            workbook=str(workbook),
            assembled_model=str(model_path),
            config_sha256=digest(cfgpath),
            source_case_provenance=str(run_dir / "MESH_CASE_PROVENANCE.json"),
            note="No OpenSees gravity cases have been solved; reaction, drift, and load-path equivalence remain unverified.",
        )
        return result
    except Exception as exc:
        record("ASSEMBLY_FAILED", error=f"{type(exc).__name__}: {exc}")
        raise
