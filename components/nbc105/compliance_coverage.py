"""NBC 105:2025 source coverage ledger — fail-closed engineering acceptance.

[REF NBC105-2025 Clauses 1–10 and Annexes A,B,C, contents pp.xiv–xx]
A module or a green software test does not prove every paragraph, table,
footnote, modelling assumption or material detail is code compliant. This
auditor explicitly separates 'heading indexed' from source-verified provisions
and independently approved native engineering evidence.

This does NOT replace professional source/provenance review and cannot grant
a whole-building approval under any input; all audit statuses remain OPEN
until a separate signed evidence process validates every provision.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

__all__=["read_source_index","audit_source_index","source_index_path","MANDATORY_GATES"]

REPO_ROOT=Path(__file__).resolve().parents[2]
SOURCE_INDEX=REPO_ROOT/"docs"/"nbc105"/"source_coverage_register.json"
MIN_SOURCE_SECTIONS=235
GROUPS={str(i) for i in range(1,11)}|{"A","B","C"}
MANDATORY_SECTION_IDS={
    "1.2","2.4.3","3.6.2","4.1.3.3","5.1.1","5.4.2.1",
    "5.5.3","7.3","7.4","7.5","8.1.3","9.2.5","9.3.2.4",
    "10.3.1","10.4","10.4.d","A.4.4.4","A.5.3","A.5.5",
    "A.5.6","B.6.1.4","B.7.1.4","C.TABLE_C_1",
}
MANDATORY_GATES=(
    "FULL_TEXT_PROVISION_AUDIT",
    "EVERY_EQUATION_AND_SOURCE_TABLE_FOOTNOTE",
    "ALL_PRODUCTION_CALL_SITES_AND_UNITS",
    "ANNEX_A_REINFORCED_CONCRETE_DETAILING",
    "ANNEX_B_STEEL_SYSTEM_DETAILING",
    "ANNEX_C_ALL_MUNICIPALITY_Z_VALUES",
    "GEOTECHNICAL_SITE_VS30_AND_FOUNDATION",
    "DESIGN_COMBINATIONS_AND_MEMBER_CAPACITY",
    "RAYLEIGH_AND_MRSM_PHYSICAL_PERIOD_PROOF",
    "NATIVE_ETABS_OPENSEES_COMPARISON",
    "DRIFT_TORSION_IRREGULARITY_AND_DISPLACEMENTS",
    "NONLINEAR_CONVERGENCE_AND_COMPLETE_CASE_EVIDENCE",
    "QUALIFIED_ENGINEER_SIGNED_DESIGN_REVIEW",
)
_ALLOWED_STATUS={"OPEN","SOURCE_CHECKED","UNIT_TEST_CHECKED",
                 "PRODUCTION_PARITY_CHECKED","NATIVE_EVIDENCE_REVIEWED"}
_MODULE_SLUGS=(
    "scope_definitions","general_principles","scope_of_analysis",
    "seismic_hazard","dynamic_characteristics","equivalent_static",
    "modal_response_spectrum","elastic_time_history",
    "nonlinear_analysis","parts_and_components",
)

def source_index_path():
    """[REF NBC105-2025 printed contents pp.xiv–xx]"""
    return SOURCE_INDEX

def read_source_index(path=None):
    """Read the exact source-index version from the local repository.

    [REF NBC105-2025 printed contents pp.xiv–xx]
    Untrusted source fields are validated by audit_source_index.
    """
    file=SOURCE_INDEX if path is None else Path(path)
    data=json.loads(file.read_text(encoding="utf-8"))
    if not isinstance(data,dict) or data.get("schema_version")!="1.0":
        raise ValueError("NBC source register schema_version must be 1.0")
    if data.get("release_status")!="NOT_CERTIFIED_SOURCE_AND_NATIVE_EVIDENCE_OPEN":
        raise ValueError("NBC source register must disclose open certification")
    return data["entries"]

def audit_source_index(records):
    """Validate 1–10 and Annex A/B/C traceability, never issue certification.

    [REF NBC105-2025 Clauses 1–10 and Annexes A–C, contents pp.xiv–xx]
    A section heading is not a complete enumeration of its normative sentences.
    At present all items remain open even when some numerical rules have tests.
    """
    if not isinstance(records,list) or not records:
        raise ValueError("NBC source index must be a nonempty list")
    required_fields={"id","group","printed_page","title","source_edition",
                     "source_review","test_ref","canonical_module",
                     "evidence_required","approval","kind"}
    seen=set();groups=set()
    for row in records:
        if not isinstance(row,dict) or not required_fields.issubset(row):
            raise ValueError("missing required source-index metadata")
        code=row["id"]
        if not isinstance(code,str) or not code.strip() or code in seen:
            raise ValueError("duplicate or invalid source-section ID")
        seen.add(code)
        group=row["group"]
        if group not in GROUPS or not code.startswith(group+"."):
            raise ValueError(f"source group / ID mismatch: {code}")
        groups.add(group)
        page=row["printed_page"]
        if type(page) is not int or not 1<=page<=130:
            raise ValueError(f"invalid printed page for {code}")
        if not isinstance(row["title"],str) or not row["title"].strip():
            raise ValueError("missing source heading title")
        if not isinstance(row["source_edition"],str) or "2025" not in row["source_edition"]:
            raise ValueError("missing 2025 code edition provenance")
        if row["source_review"]!="HEADING_INDEXED_REQUIREMENT_TEXT_NOT_EXHAUSTIVELY_VERIFIED":
            raise ValueError("source-index heading is not full text compliance approval")
        if row["approval"] not in _ALLOWED_STATUS:
            raise ValueError(f"invalid approval state for {code}")
        if not isinstance(row["evidence_required"],str) or not row["evidence_required"].strip():
            raise ValueError(f"missing native/engineering evidence requirement for {code}")
        if group in set(str(i) for i in range(1,11)):
            g=int(group)
            expected=f"components/nbc105/clause_{g:02d}_{_MODULE_SLUGS[g-1]}.py"
            if row["canonical_module"]!=expected:
                raise ValueError(f"clause module mismatch for {code}")
            if not (REPO_ROOT/expected).is_file():
                raise ValueError(f"clause module not present: {expected}")
        elif row["canonical_module"] is not None:
            raise ValueError(f"Annex {group} cannot falsely claim clause module ownership")
        if row["test_ref"] is not None:
            test=row["test_ref"]
            if (not isinstance(test,str) or not test.startswith("tests/")
                or ".." in Path(test).parts or not (REPO_ROOT/test).is_file()):
                raise ValueError(f"missing source test for {code}: {test}")
    missing=MANDATORY_SECTION_IDS-seen
    if missing:
        raise ValueError("missing mandatory NBC source subsection IDs: "+", ".join(sorted(missing)))
    if len(records)<MIN_SOURCE_SECTIONS:
        raise ValueError(f"missing source coverage rows: {len(records)} < {MIN_SOURCE_SECTIONS}")
    if groups!=GROUPS:
        raise ValueError("missing source annex or clause groups: "+str(sorted(GROUPS-groups)))
    counts=Counter(x["group"] for x in records)
    statuses=Counter(x["approval"] for x in records)
    return {
        "standard":"NBC 105:2025",
        "index_scope":"PRINTED_SECTION_HEADINGS_ONLY_NOT_EVERY_SENTENCE",
        "approval":"NOT_CERTIFIED_SOURCE_AND_NATIVE_EVIDENCE_OPEN",
        "groups":{g:counts[g] for g in sorted(GROUPS)},
        "total_indexed_sections":len(records),
        "indexed_ids":sorted(seen),
        "open_requirements":len(records),
        "source_status_counts":dict(statuses),
        "mandatory_gates":list(MANDATORY_GATES),
        "explanation":(
            "All 10 clauses and Annexes A/B/C have indexed headings. "
            "Their detailed normative sentences, notes, illustrations, "
            "source-table footnotes, all active call paths and native "
            "structural design evidence have NOT all been verified. "
            "No automatic code/building approval is permitted."
        ),
    }
