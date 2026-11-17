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
    """SHA256 source-file identity. [REF docs/source/components/gravity/mesh_cases.py.md]"""
    return sha256(Path(path).read_bytes()).hexdigest()


def _refuse_linked_chain(path):
    """Check existing path components before resolving a selected source/output.

    A mesh staging operation must not silently traverse linked ETABS source
    data, prepared configurations or folders outside the selected export.
    """
    candidate = Path(path).expanduser()
    for part in (candidate, *candidate.parents):
        if part.is_symlink():
            raise ValueError("Refusing linked mesh source/output path: " + str(candidate))
    return candidate


def _read_source_manifest(folder):
    """Preflight every available source file before creating a new mesh run."""
    original = {}
    for name in REQUIRED_SOURCE + OPTIONAL_SOURCE:
        source = _refuse_linked_chain(folder / name)
        if not source.exists():
            if name in REQUIRED_SOURCE:
                raise FileNotFoundError("Missing required ETABS audit input: " + name)
            continue
        if not source.is_file():
            raise ValueError("Not a regular ETABS audit source: " + name)
        original[name] = digest(source)
    return original


def validated_mesh_size(subdivisions):
    """Strict mesh identity; accept exact GUI integers, never truncate floats.

    [REF docs/source/components/gravity/mesh_cases.py.md] Case provenance contract.
    """
    if isinstance(subdivisions, bool):
        raise ValueError("Mesh subdivision must be an exact integer: 4, 8 or 16")
    if type(subdivisions) is int:
        n = subdivisions
    elif isinstance(subdivisions, str) and subdivisions in ("4", "8", "16"):
        n = int(subdivisions)
    else:
        raise ValueError("Mesh subdivision must be an exact integer: 4, 8 or 16")
    if n not in MESH_SIZES:
        raise ValueError("Mesh comparison supports only 4, 8 and 16 subdivisions")
    return n


def case_base(folder, subdivisions):
    """Independent case directory. [REF docs/source/components/gravity/mesh_cases.py.md]"""
    n = validated_mesh_size(subdivisions)
    return Path(folder) / "02_MODEL" / "SLAB_LOAD_PATH" / f"MESH_{n:02d}"


def prepared_configs(folder):
    """Create three labeled *configurations*, not completed analysis cases.
    [REF docs/source/components/gravity/mesh_cases.py.md]
    """
    folder = _refuse_linked_chain(folder).resolve(strict=True)
    config_path = _refuse_linked_chain(folder / REQUIRED_SOURCE[3])
    if not config_path.is_file():
        raise FileNotFoundError("Export the ETABS source model and config first.")
    cfg = json.loads(config_path.read_text(encoding="utf-8-sig"))
    target_dir = folder / "02_MODEL" / "SLAB_LOAD_PATH" / "PREPARED_CONFIGS"
    _refuse_linked_chain(target_dir)
    # Preflight *all* destinations before writing any derived config.
    targets = [
        _refuse_linked_chain(target_dir / f"Model_Config_MESH_{n:02d}.json")
        for n in MESH_SIZES
    ]
    target_dir.mkdir(parents=True, exist_ok=True)
    result = []
    for n, target in zip(MESH_SIZES, targets):
        prepared = dict(cfg, floor_subdivisions=n)
        # No output implies an assembled/solved case. Replacements here are
        # config-only and checked again when copied to a unique run directory.
        target.write_text(json.dumps(prepared, indent=2, ensure_ascii=False), encoding="utf-8")
        result.append(target)
    return result


def stage_case(folder, subdivisions):
    """Copy source inputs into an isolated, unique case run; never mutate root.
    [REF docs/source/components/gravity/mesh_cases.py.md]
    """
    folder = _refuse_linked_chain(folder).resolve(strict=True)
    n = validated_mesh_size(subdivisions)
    parent = case_base(folder, n) / "RUNS"
    # Verify the entire path before any mkdir/copy. The config is source
    # evidence and the newly staged config is intentionally a derived variant.
    _refuse_linked_chain(parent)
    source_digests = _read_source_manifest(folder)
    root_config = json.loads((folder / REQUIRED_SOURCE[3]).read_text(encoding="utf-8-sig"))
    prepared = _refuse_linked_chain(
        folder / "02_MODEL" / "SLAB_LOAD_PATH" / "PREPARED_CONFIGS"
        / f"Model_Config_MESH_{n:02d}.json")
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
    for filename, original_sha in source_digests.items():
        source = _refuse_linked_chain(folder / filename)
        target = _refuse_linked_chain(run_dir / filename)
        shutil.copy2(source, target)
        staged_sha = digest(target)
        # Detect source changes during staging, not only changes in the copy.
        if staged_sha != original_sha or digest(source) != original_sha:
            raise RuntimeError("ETABS source changed during mesh staging: " + filename)
        provenance[filename] = staged_sha
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
        "original_source_file_sha256": source_digests,
        "meaning": "ETABS saved source audit copied to mesh-specific folder; no solver executed",
    }
    (run_dir / "MESH_CASE_PROVENANCE.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return run_dir


def package_mesh_case(folder, subdivisions):
    """Package one independent mesh case without merging distinct run identities.

    A ZIP is a diagnostic export, not evidence of a completed gravity solve.

    [REF docs/source/components/gravity/mesh_cases.py.md]
    Store it at 02_MODEL/SLAB_LOAD_PATH/UPLOAD_PACKAGES/MESH_nn.zip.
    Existing case data are read-only; symlinks and recursive uploads refused.
    """
    import zipfile
    root=_refuse_linked_chain(folder).resolve(strict=True)
    n=validated_mesh_size(subdivisions)
    case=_refuse_linked_chain(case_base(root,n))
    if not case.is_dir():
        raise FileNotFoundError(f"MESH_{n:02d} case has no outputs to package")
    output=root/"02_MODEL"/"SLAB_LOAD_PATH"/"UPLOAD_PACKAGES"/f"MESH_{n:02d}.zip"
    _refuse_linked_chain(output)
    # Do not label an in-progress write as a complete debugging snapshot.
    for status_path in case.glob("RUNS/RUN_*/MESH_BUILD_STATUS.json"):
        _refuse_linked_chain(status_path)
        state=json.loads(status_path.read_text(encoding="utf-8-sig")).get("status")
        if state in {"ASSEMBLY_RUNNING","MODEL_ASSEMBLED_FORMULA_EXPORT_RUNNING"}:
            raise RuntimeError("Mesh run is still writing: "+str(status_path.parent))
    files=[]
    for p in sorted(case.rglob("*")):
        _refuse_linked_chain(p)
        if p.is_file() and not p.name.endswith(".processing.json"):
            files.append(p)
    if not files:
        raise ValueError(f"MESH_{n:02d} has no saved files")
    output.parent.mkdir(parents=True,exist_ok=True)
    # A unique same-directory staging name prevents a second ZIP click
    # from corrupting an in-progress archive; replace only after validation.
    temporary=output.with_name(output.name+".tmp-"+uuid4().hex)
    _refuse_linked_chain(temporary)
    manifest={"mesh_subdivisions":n,
              "status":"DIAGNOSTIC_PACKAGE_NOT_SOLVER_ACCEPTANCE",
              "files":{p.relative_to(case).as_posix():digest(p) for p in files}}
    try:
        with zipfile.ZipFile(temporary,"w",compression=zipfile.ZIP_DEFLATED,
                             compresslevel=6,allowZip64=True) as z:
            for p in files:
                z.write(p,arcname=f"MESH_{n:02d}/"+p.relative_to(case).as_posix())
            z.writestr(f"MESH_{n:02d}/ZIP_SHA256_MANIFEST.json",
                       json.dumps(manifest,indent=2))
        with zipfile.ZipFile(temporary) as check:
            bad=check.testzip()
            if bad:raise IOError("ZIP checksum failed: "+bad)
            for name,expected in manifest["files"].items():
                checksum=sha256()
                with check.open(f"MESH_{n:02d}/"+name) as stream:
                    for block in iter(lambda:stream.read(1024*1024),b""):
                        checksum.update(block)
                if checksum.hexdigest()!=expected:
                    raise IOError("Source file changed during ZIP assembly: "+name)
        temporary.replace(output)
    finally:
        if temporary.exists():temporary.unlink()
    return output


def recover_assembled_mesh_workbook(folder, subdivisions, *, progress=None):
    """Re-export a workbook without reassembling an already verified mesh.

    Model and saved configuration SHA must match, and the original source
    hashes must still match the staged run's source manifest. This is a
    spreadsheet recovery only, NOT gravity convergence/ETABS acceptance.

    [REF docs/source/components/gravity/mesh_cases.py.md]
    """
    root=_refuse_linked_chain(folder).resolve(strict=True)
    n=validated_mesh_size(subdivisions)
    case=case_base(root,n)
    parent=_refuse_linked_chain(case/"RUNS")
    if not parent.is_dir():
        raise FileNotFoundError(f"No independent MESH_{n:02d} runs exist")
    runs=sorted((p for p in parent.iterdir() if p.is_dir() and
                 p.name.startswith("RUN_")),key=lambda p:p.name,reverse=True)
    for run in runs:
        _refuse_linked_chain(run)
        model=run/"OpenSees_Complete_Model_Data_V118.json"
        cfg_file=run/REQUIRED_SOURCE[3]
        provenance=run/"MESH_CASE_PROVENANCE.json"
        if not all(p.is_file() for p in (model,cfg_file,provenance)):
            continue
        meta=json.loads(provenance.read_text(encoding="utf-8-sig"))
        if meta.get("mesh_subdivisions")!=n:
            raise ValueError("Mesh run identity disagrees with selected mesh")
        before=meta.get("original_source_file_sha256",{})
        if not before or any(not (root/name).is_file() or
                             digest(root/name)!=saved_sha
                             for name,saved_sha in before.items()):
            raise ValueError("Original ETABS source audit changed; do not re-export stale mesh run")
        staged_cfg=json.loads(cfg_file.read_text(encoding="utf-8-sig"))
        root_cfg=json.loads((root/REQUIRED_SOURCE[3]).read_text(encoding="utf-8-sig"))
        if staged_cfg!=dict(root_cfg,floor_subdivisions=n):
            raise ValueError("Staged mesh config no longer matches source settings")
        assembled=json.loads(model.read_text(encoding="utf-8-sig"))
        if assembled.get("config_sha256")!=digest(cfg_file):
            raise ValueError("Assembled mesh SHA/config mismatch; do not reuse this model")
        if not any(e.get("category")=="FLOOR" for e in assembled.get("shells",[])):
            raise ValueError("Assembled model contains no FLOOR shell cells")
        from OpenSees_Load_Path_V141 import export
        kwargs={'output_root':case}
        if progress is not None:
            kwargs['progress']=progress
        workbook=export(run,**kwargs)
        status=dict(status="FORMULA_WORKBOOK_REEXPORTED_NOT_GRAVITY_VERIFIED",
                    mesh_subdivisions=n,workbook=str(workbook),
                    assembled_model=str(model),config_sha256=digest(cfg_file),
                    run_directory=str(run),
                    note="Reused matching assembled mesh; NO native gravity or ETABS comparison")
        (run/"MESH_BUILD_STATUS.json").write_text(
            json.dumps(status,indent=2),encoding="utf-8")
        return status
    raise FileNotFoundError(
        f"No completed SHA-matched assembled MESH_{n:02d} run found. Build the mesh first.")


def build_case(folder, subdivisions, *, runtime_dir=None, progress=None):
    """Stage, assemble fresh mesh and export formula workbook for that mesh only.

    This is intentionally a potentially expensive operation and must run in a
    GUI worker thread. Other native solver stages, gravity and ETABS parity
    remain separate. On failure keep the case run + error JSON for diagnosis.
    [REF docs/source/components/gravity/mesh_cases.py.md]
    """
    import time
    from time import perf_counter
    n = validated_mesh_size(subdivisions)
    started = perf_counter()
    run_dir = None
    def emit(message):
        if run_dir is not None:
            with (run_dir/'MESH_RUN.log').open('a',encoding='utf-8') as stream:
                stream.write(f'[{perf_counter()-started:.1f}s] {message}\n')
        if callable(progress):
            progress(message, perf_counter()-started)
    emit(f'MESH_{n:02d}: verifying source SHA and copying inputs')
    run_dir = stage_case(folder, subdivisions)
    import sys
    identity=dict(python_executable=sys.executable,python_version=sys.version,
                  mesh_cases_path=str(Path(__file__).resolve()),
                  mesh_cases_disk_sha256=digest(__file__),
                  hash_scope="Current disk files; restart Python after updates. Not an in-memory code attestation.")
    (run_dir/'MESH_RUNTIME_IDENTITY.json').write_text(
        json.dumps(identity,indent=2),encoding='utf-8')
    emit(f"Runtime Python: {sys.executable}; mesh code: {identity['mesh_cases_path']}")
    emit(f'MESH_{n:02d}: inputs staged; starting independent full-model assembly')
    log = run_dir / "MESH_BUILD_STATUS.json"
    def record(status, **extra):
        report = dict(mesh_subdivisions=n, status=status, run_directory=str(run_dir),
                      updated_utc=datetime.now(timezone.utc).isoformat(), **extra)
        log.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        return report
    record("ASSEMBLY_RUNNING")
    assembly_started = perf_counter()
    assembly_complete=False
    try:
        from OpenSees_Complete_Export_V118 import prepare_complete_export
        import inspect
        assembly_file=Path(inspect.getsourcefile(inspect.unwrap(prepare_complete_export))).resolve()
        identity.update(assembly_path=str(assembly_file),assembly_disk_sha256=digest(assembly_file))
        (run_dir/'MESH_RUNTIME_IDENTITY.json').write_text(
            json.dumps(identity,indent=2),encoding='utf-8')
        emit(f'Assembly code: {assembly_file}')
        if runtime_dir is None:
            # This package may be loaded through legacy compatibility facades;
            # resolve runtime from the real source module rather than cwd.
            from components.model import assembly
            runtime_dir = Path(assembly.__file__).resolve().parents[2]
        manifest, report = prepare_complete_export(
            str(run_dir), runtime_dir=Path(runtime_dir), progress=emit)
        emit(f'MESH_{n:02d}: assembly completed in {perf_counter()-assembly_started:.1f}s; checking result')
        if report.get("assembly_errors") or not manifest.get("elastic_assembled"):
            raise RuntimeError("Mesh assembly blocked: " + "; ".join(report.get("assembly_errors", [])))
        # Verify that the model identity was derived from this run's saved cfg.
        model_path = run_dir / "OpenSees_Complete_Model_Data_V118.json"
        data = json.loads(model_path.read_text(encoding="utf-8-sig"))
        cfgpath = run_dir / REQUIRED_SOURCE[3]
        if data.get("config_sha256") != digest(cfgpath):
            raise RuntimeError("Mesh model/config SHA256 disagreement after assembly; no workbook exported.")
        cfg = json.loads(cfgpath.read_text(encoding="utf-8-sig"))
        try:
            assembled_n = validated_mesh_size(cfg.get("floor_subdivisions"))
        except ValueError as exc:
            raise RuntimeError("Mesh size not preserved by model assembly.") from exc
        if assembled_n != n:
            raise RuntimeError("Mesh size was not preserved by model assembly.")
        assembly_complete=True
        record("MODEL_ASSEMBLED_FORMULA_EXPORT_RUNNING",
               assembled_model=str(model_path),config_sha256=digest(cfgpath))
        from OpenSees_Load_Path_V141 import export
        emit(f'MESH_{n:02d}: writing full formula workbook (may be large)')
        workbook_started = perf_counter()
        workbook = export(run_dir, output_root=case_base(folder, n), progress=emit)
        emit(f'MESH_{n:02d}: workbook completed in {perf_counter()-workbook_started:.1f}s')
        result = record(
            "FORMULA_WORKBOOK_CREATED_NOT_GRAVITY_VERIFIED",
            workbook=str(workbook),
            assembled_model=str(model_path),
            config_sha256=digest(cfgpath),
            source_case_provenance=str(run_dir / "MESH_CASE_PROVENANCE.json"),
            note="No OpenSees gravity cases have been solved; reaction, drift, and load-path equivalence remain unverified.",
        )
        emit(f'MESH_{n:02d}: complete in {perf_counter()-started:.1f}s')
        return result
    except Exception as exc:
        import traceback
        (run_dir/'MESH_FAILURE_TRACEBACK.txt').write_text(traceback.format_exc(),encoding='utf-8')
        emit(f'FAILED: {type(exc).__name__}: {exc}')
        record("WORKBOOK_EXPORT_FAILED_MODEL_ASSEMBLED" if assembly_complete
               else "ASSEMBLY_FAILED", error=f"{type(exc).__name__}: {exc}")
        raise


def main(argv=None):
    """Recover a SHA-matched saved mesh workbook without Tk or rebuilding.

    REF docs/source/components/gravity/mesh_cases.py.md. No solver is run.
    """
    import argparse
    parser=argparse.ArgumentParser(description='Recover Excel from a saved independent mesh assembly')
    parser.add_argument('folder',type=Path,help='Original ETABS export root')
    parser.add_argument('--mesh',required=True,choices=('4','8','16'))
    args=parser.parse_args(argv)
    result=recover_assembled_mesh_workbook(args.folder,args.mesh,
                                          progress=lambda message:print(message,flush=True))
    print(json.dumps(result,indent=2),flush=True)
    return result


if __name__=='__main__':
    main()
