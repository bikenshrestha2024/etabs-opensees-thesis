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
    if not path.is_file():
        return None
    with path.open("rb") as stream:
        return hashlib.file_digest(stream,"sha256").hexdigest()


def recorded_result_model_sha(result_path, case=None):
    """[REF docs/source/components/validation/saved_case_identity.py.md]
    Look up an explicitly recorded source-model hash, never infer from names.

    Result source is trusted only when a valid hexadecimal SHA256 was emitted
    by the analysis producer. Historical source labels stay NOT_VERIFIED.
    """
    path=Path(result_path).expanduser().resolve()
    folder=path.parent
    # Canonical case outputs place the immutable input manifest alongside
    # numeric results. No filesystem modifications are made.
    for parent in (folder,*folder.parents):
        candidate=parent/"00_INPUT_SOURCE"/"CASE_MANIFEST.json"
        if candidate.is_file():
            try:
                item=json.loads(candidate.read_text(encoding="utf-8-sig"))
                digest=item.get("model_sha256")
                if _valid_sha256(digest):
                    return digest.lower()
            except (OSError,ValueError,TypeError):
                pass
            break
        if parent.name.casefold() in {
                "05_mrsm","03_esm","06_linear_time_history",
                "07_nonlinear_time_history","opensees_analysis_results"}:
            break
    try:
        if path.name=="MRSM_Results_V132.json" and case:
            content=json.loads(path.read_text(encoding="utf-8-sig"))
            value=content.get(str(case),{}).get("model_sha256")
            if _valid_sha256(value):
                return value.lower()
        if path.name.startswith("Deformation_") and path.suffix.lower()==".json":
            value=json.loads(path.read_text(encoding="utf-8-sig")).get("model_sha256")
            if _valid_sha256(value):
                return value.lower()
        if path.name.startswith("Drift_Check_"):
            suffix=path.stem.removeprefix("Drift_Check_")
            metadata=folder/("NBC105_ESM_OpenSees_Response_META_"+suffix+".json")
            if metadata.is_file():
                value=json.loads(metadata.read_text(encoding="utf-8-sig")).get("model_sha256")
                if _valid_sha256(value):
                    return value.lower()
    except (OSError,ValueError,TypeError,AttributeError):
        pass
    return None


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
            cache[key]=recorded_result_model_sha(path,item.get("case"))
        found=cache[key]
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
