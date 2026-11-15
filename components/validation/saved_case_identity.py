"""Model-identity-aware read-only verification for saved seismic responses.

[REF docs/source/components/validation/saved_case_identity.py.md]
A source .EDB file is NOT equivalent to an exported model JSON fingerprint.
Compare only serialized OpenSees model SHA256 with the same file basis.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

_SHA256 = re.compile(r"[0-9a-fA-F]{64}")


def _valid_sha256(value):
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


def current_export_model_sha(export_dir):
    """[REF docs/source/components/validation/saved_case_identity.py.md]
    Fingerprint the selected active serialized model, if available.
    """
    from components.inputs.output_layout import export_root_for
    root=export_root_for(export_dir)
    path=root/"OpenSees_Complete_Model_Data_V118.json"
    if path.is_symlink():
        # Never fingerprint an external file through a linked source alias.
        return None
    if not path.is_file():
        return None
    with path.open("rb") as stream:
        return hashlib.file_digest(stream,"sha256").hexdigest()


def source_model_hash_evidence(result_path, case=None):
    """[REF docs/source/components/validation/saved_case_identity.py.md]
    Independently inspect run manifest AND recorded numeric payload SHA256.

    If both are valid but disagree, report an explicit source conflict.
    Neither the run directory nor an old saved report is modified.
    """
    raw_path=Path(result_path).expanduser()
    # Resolving first would erase evidence of a linked source payload.
    linked_source=any(part.is_symlink() for part in (raw_path,*raw_path.parents))
    path=raw_path.resolve()
    folder=path.parent
    manifest_digest=None
    payload_digest=None
    invalid_manifest=False
    invalid_payload_sha=False
    manifest_path=None
    for parent in (folder,*folder.parents):
        candidate=parent/"00_INPUT_SOURCE"/"CASE_MANIFEST.json"
        if candidate.is_symlink():
            invalid_manifest=True
            manifest_path=str(candidate)
            break
        if candidate.is_file():
            manifest_path=str(candidate)
            try:
                item=json.loads(candidate.read_text(encoding="utf-8-sig"))
                value=item.get("model_sha256") if isinstance(item,dict) else None
                if _valid_sha256(value):
                    manifest_digest=value.lower()
                else:
                    invalid_manifest=True
            except (OSError,ValueError,TypeError,AttributeError):
                invalid_manifest=True
            break
        if parent.name.casefold() in {
                "05_mrsm","03_esm","06_linear_time_history",
                "07_nonlinear_time_history","opensees_analysis_results"}:
            break
    try:
        value=None
        if path.name=="MRSM_Results_V132.json" and case:
            content=json.loads(path.read_text(encoding="utf-8-sig"))
            if isinstance(content,dict) and isinstance(content.get(str(case)),dict):
                value=content[str(case)].get("model_sha256")
        elif path.name.startswith("Deformation_") and path.suffix.lower()==".json":
            content=json.loads(path.read_text(encoding="utf-8-sig"))
            value=content.get("model_sha256") if isinstance(content,dict) else None
        elif path.name.startswith("Drift_Check_"):
            suffix=path.stem.removeprefix("Drift_Check_")
            metadata=folder/("NBC105_ESM_OpenSees_Response_META_"+suffix+".json")
            if metadata.is_symlink():
                linked_source=True
            elif metadata.is_file():
                content=json.loads(metadata.read_text(encoding="utf-8-sig"))
                value=content.get("model_sha256") if isinstance(content,dict) else None
        if value is not None:
            if _valid_sha256(value):
                payload_digest=value.lower()
            else:
                invalid_payload_sha=True
    except (OSError,ValueError,TypeError,AttributeError):
        pass
    conflict=(manifest_digest is not None and payload_digest is not None
              and manifest_digest!=payload_digest)
    return {"manifest_model_sha256":manifest_digest,
            "payload_model_sha256":payload_digest,
            "manifest_path":manifest_path,
            "invalid_manifest":invalid_manifest,
            "invalid_payload_sha":invalid_payload_sha,
            "linked_source":linked_source,
            "conflict":conflict,
            "model_sha256":None if conflict or invalid_manifest or
                           invalid_payload_sha or linked_source else
                           payload_digest or manifest_digest}


def recorded_result_model_sha(result_path, case=None):
    """[REF docs/source/components/validation/saved_case_identity.py.md]
    Return an unambiguous saved SHA, or None on a source-evidence conflict.
    """
    return source_model_hash_evidence(result_path,case)["model_sha256"]


def identity_screen(rows, *, expected_model_sha):
    """[REF docs/source/components/validation/saved_case_identity.py.md]
    Annotate review-only rows; omit proven mismatches from plotted results.

    Missing hash is kept with NOT_VERIFIED and an explicit warning. Full
    structural validation requires EDB, stiffness, mass, boundary and load
    comparison beyond a matching serialized source-model hash.
    """
    selected=[]
    issues=[]
    cache={}
    for row in rows:
        item=dict(row)
        path=item.get("file")
        if not path:
            item["source_identity_status"]="NOT_VERIFIED"
            selected.append(item)
            continue
        key=(str(path),str(item.get("case","")))
        if key not in cache:
            cache[key]=source_model_hash_evidence(path,item.get("case"))
        evidence=cache[key]
        if evidence["linked_source"]:
            issues.append({
                "status":"LINKED_RESULT_EVIDENCE_EXCLUDED",
                "file":str(path),"case":item.get("case"),
                "reason":"Linked source result or ESM metadata cannot establish source-model identity.",
            })
            continue
        if evidence["invalid_payload_sha"]:
            issues.append({
                "status":"INVALID_RESULT_MODEL_SHA_EXCLUDED",
                "file":str(path),"case":item.get("case"),
                "reason":"An explicitly recorded malformed model SHA cannot be ignored in favor of manifest-only identity.",
            })
            continue
        if evidence["invalid_manifest"]:
            issues.append({
                "status":"INVALID_RUN_MANIFEST_EXCLUDED",
                "file":str(path),"case":item.get("case"),
                "manifest":evidence["manifest_path"],
                "reason":"Canonical run manifest is malformed, unreadable, or linked; do not promote a payload hash to verified model identity.",
            })
            continue
        if evidence["conflict"]:
            issues.append({
                "status":"SOURCE_MANIFEST_RESULT_SHA_CONFLICT_EXCLUDED",
                "file":str(path),"case":item.get("case"),
                "manifest_model_sha256":evidence["manifest_model_sha256"],
                "payload_model_sha256":evidence["payload_model_sha256"],
                "reason":"Run manifest disagrees with numeric result source; file excluded from plots until independently reconciled.",
            })
            continue
        found=evidence["model_sha256"]
        if not expected_model_sha or not found:
            item["source_identity_status"]="NOT_VERIFIED"
            selected.append(item)
        elif found.lower()!=expected_model_sha.lower():
            issues.append({
                "status":"SOURCE_MODEL_SHA_MISMATCH_EXCLUDED",
                "file":str(path),"case":item.get("case"),
                "result_model_sha256":found,
                "selected_export_model_sha256":expected_model_sha,
                "reason":"This response belongs to a different serialized model; excluded from plots. Historical file remains unchanged.",
            })
        else:
            item["source_identity_status"]="MATCHED_SERIALIZED_MODEL_SHA_NOT_ETABS_EQUIVALENCE"
            selected.append(item)
    return selected,issues
