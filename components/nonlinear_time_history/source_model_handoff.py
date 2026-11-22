"""Source-frozen NLTHA model handoff and literature section inventory.

[REF docs/source/components/nonlinear_time_history/source_model_handoff.py.md]
The original ETABS-derived OpenSees export is immutable. No fabricated
reinforcement, material parameters, MPC transfers, or physical acceptance.
"""
from __future__ import annotations
import hashlib
import json
import math
import shutil
from collections import Counter
from pathlib import Path

REQUIRED_SOURCE_FILES = (
    "OpenSees_Complete_Model_Data_V118.json",
    "OpenSees_Complete_Model_Config_V118.json",
    "OpenSees_Complete_Export_Report_V118.json",
    "OpenSees_Load_Conversion_Audit.json",
    "OpenSees_Source_Model_Metadata_V118.json",
    "OpenSees_Element_Connectivity.json",
)
OPTIONAL_SOURCE_FILES = (
    "OpenSees_Complete_Story_Masters_V118.csv",
    "OpenSees_Element_Overrides_V125.json",
    "OpenSees_Complete_Element_Map_V118.json",
)


def source_sha256(path):
    """[REF docs/source/components/nonlinear_time_history/source_model_handoff.py.md]
    Hash local source bytes without uploading them to GitHub or a service."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def required_source_files(source):
    """[REF docs/source/components/nonlinear_time_history/source_model_handoff.py.md]
    Ensure all primary 32-support topology inputs exist before writing outputs."""
    source=Path(source).expanduser().resolve()
    if not source.is_dir():
        raise FileNotFoundError("Existing OpenSees model folder missing: " + str(source))
    for filename in REQUIRED_SOURCE_FILES:
        if not (source / filename).is_file():
            raise FileNotFoundError("Required NLTHA source file missing: " + str(source / filename))
    return source


def stage_existing_model_sources(source, destination):
    """[REF docs/source/components/nonlinear_time_history/source_model_handoff.py.md]
    Copy exact source inputs into one isolated NLTHA run; verify byte hashes.

    No edits to user source; refuses to overwrite preexisting different copies.
    Model reassembly is performed separately by the existing builder.
    """
    source=required_source_files(source)
    destination=Path(destination).expanduser().resolve()
    if source==destination:
        raise ValueError("NLTHA model destination must differ from source")
    fingerprints={}
    selected=[*REQUIRED_SOURCE_FILES]
    selected.extend(filename for filename in OPTIONAL_SOURCE_FILES
                    if (source/filename).is_file())
    for filename in selected:
        current=source_sha256(source/filename)
        if (destination/filename).exists() and source_sha256(destination/filename)!=current:
            raise FileExistsError("Refusing to overwrite different staged source: "+str(destination/filename))
        fingerprints[filename]=current
    destination.mkdir(parents=True, exist_ok=True)
    for filename in selected:
        output=destination/filename
        if not output.exists():
            shutil.copy2(source/filename,output)
        if source_sha256(output)!=fingerprints[filename]:
            raise IOError("NLTHA isolated copy SHA mismatch: "+filename)
    return fingerprints


def solver_reaction_support_tags(report, support_case="PHYSICAL_32"):
    """[REF docs/source/components/nonlinear_time_history/source_model_handoff.py.md]
    Use only actual assembled OpenSees base supports; not 76 exported point rows.

    Native ETABS edge/MPC transfer remains unverified even if tags match.
    """
    from components.model.support_case_contract import (
        normalize_support_case, require_runtime_support_case
    )
    selected=normalize_support_case(support_case)
    require_runtime_support_case(selected,report)
    raw=report["gravity_base_support_tags"]
    if any(isinstance(tag,bool) for tag in raw):
        raise ValueError("Boolean solver support tag invalid")
    tags=sorted(int(tag) for tag in raw)
    if len(set(tags))!=len(tags):
        raise ValueError("Duplicate actual solver support tag")
    return tags


def literature_section_inventory(data, config):
    """[REF docs/source/components/nonlinear_time_history/source_model_handoff.py.md]
    Create a non-approving, geometry-bound frame/wall/source literature ledger.

    Frame dimensions/rebar cards originate from existing repository templates;
    NOT an experimental specimen or source ETABS bar schedule.
    """
    from components.sections.definitions import RC_SECTION_CONFIG, SECTION_TAGS
    if not isinstance(data,dict) or not isinstance(config,dict):
        raise TypeError("OpenSees model data/config must be JSON objects")
    frames=data.get("frames",[])
    shells=data.get("shells",[])
    mapping=config.get("frame_section_mapping") or {}
    if not isinstance(mapping,dict):
        raise ValueError("frame_section_mapping must be an object")
    counts=Counter()
    families={}
    for item in frames:
        category=item.get("category")
        name=(item.get("properties") or {}).get("section")
        if not name:
            raise ValueError("Source frame has no original ETABS section name")
        counts[name]+=1
        families.setdefault(name,set()).add(category)
    result={}
    for name in sorted(counts):
        target=mapping.get(name)
        if not isinstance(target,str) or not target or target not in SECTION_TAGS:
            raise ValueError("Unmapped source frame section: "+str(name))
        template=RC_SECTION_CONFIG.get(target)
        # Braces do not use RC confinement; preserve existing steel section tag.
        result[name]=dict(
            source_section=name,solver_section_name=target,
            solver_section_tag=SECTION_TAGS[target],
            member_count=counts[name],categories=sorted(map(str,families[name])),
            research_template={
                key:template.get(key) for key in (
                    "width_mm","depth_mm","cover_mm","tie_diameter_mm",
                    "bar_diameter_mm","bars_per_side","cover_fc_mpa",
                    "core_fcc_mpa","fy_rebar_mpa","E0_mpa")
                if template is not None
            } if template else None,
            assignment_status="ILLUSTRATIVE_SECTION_NOT_PROJECT_REINFORCEMENT"
        )
    walls={}
    for item in shells:
        if item.get("category")!="SHEAR WALL":
            continue
        props=item.get("properties") or {}
        name=props.get("property")
        if not name:
            raise ValueError("Source shear wall missing property name")
        thick=props.get("thickness")
        if isinstance(thick,bool) or not isinstance(thick,(int,float)) or not math.isfinite(thick) or thick<=0:
            raise ValueError("Source shear wall thickness missing or nonpositive: "+name)
        current=walls.get(name)
        if current and (current["thickness_m"]!=thick or current["source_concrete"]!=props.get("material")):
            raise ValueError("Mixed thickness/material under same wall property: "+name)
        if not current:
            current=dict(thickness_m=thick,source_concrete=props.get("material"),
                         source_property=name,panel_count=0)
            walls[name]=current
        current["panel_count"]+=1
    reviewed=config.get("nonlinear_parameters_reviewed") is True
    configured=bool(config.get("nonlinear_materials_file")) and bool(config.get("nonlinear_wall_fsam_tags"))
    return dict(
        status=("PROJECT_CARDS_EXIST_REQUIRE_INDEPENDENT_CALIBRATION"
                if reviewed and configured else "RESEARCH_TEMPLATE_UNCALIBRATED"),
        project_materials_calibrated=False,
        source_model_scope="EXISTING_ETABS_DERIVED_OPENSEES_EXPORT",
        frame_sections=result,wall_properties=walls,
        adopted_literature_formulations=[
            {"id":"R01","model":"ConcreteCM/SteelMPF/FSAM",
             "url":"https://peer.berkeley.edu/publications/2015-12",
             "role":"Specimen-derived research baseline; not source building reinforcement"},
            {"id":"R02","model":"E_SFI_MVLEM_3D",
             "url":"https://doi.org/10.1016/j.engstruct.2023.116700",
             "role":"Nonlinear wall shear-flexure model; not building acceptance"},
            {"id":"OpenSees","model":"forceBeamColumn/Fiber",
             "url":"https://opensees.github.io/OpenSeesDocumentation/",
             "role":"Frame nonlinear section and integration formulation"}
        ],
        warnings=[
            "Actual ETABS M45 concrete properties may not match M35/Fe550 illustrative frame fiber cards.",
            "Source walls require their own verified reinforcement and FSAM orientation/region mapping.",
            "A paper's measured specimen constants do not establish actual 25-storey member calibration.",
            "All native E-SFI material, wall openings, damping, connection and support transfers remain review gates."
        ],
    )
