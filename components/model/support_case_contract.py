"""One physical support-case contract shared by ESM, Rayleigh, modal, MRSM, LTHA and NLTHA.

[REF engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md]
[REF components/model/assembly.py build_complete_model]

32 exact foundation joints are USER-CONFIRMED. The other 44 exported
source-restraint IDs are SHEAR-WALL MESH POINTS, not independent foundations.
Changing fixities here does not reconstruct missing ETABS auto-edge/MPC
constraints or prove the solver's native equivalence.
"""
from __future__ import annotations

from components.gravity.etabs_reaction_support_filter import PROJECT_PRIMARY_32

DEFAULT_SUPPORT_CASE = "PHYSICAL_32"
CHOICES = ("PHYSICAL_32", "SOURCE_76", "WALL_BASE_97")
UI_CHOICES = (
    ("32 physical foundation supports (primary)", "PHYSICAL_32"),
    ("76 source restraint points (diagnostic)", "SOURCE_76"),
    ("97 idealized wall-base restraints (diagnostic)", "WALL_BASE_97"),
)
_ALIASES = {
    "32": "PHYSICAL_32", "PHYSICAL_32": "PHYSICAL_32",
    "76": "SOURCE_76", "SOURCE_76": "SOURCE_76",
    "97": "WALL_BASE_97", "WALL_BASE_97": "WALL_BASE_97",
}


def normalize_support_case(value):
    """Normalize only explicit, enumerated support scenarios.

    [REF engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md §A]
    """
    key=DEFAULT_SUPPORT_CASE if value is None else str(value).strip().upper()
    if key not in _ALIASES:
        raise ValueError("Unknown support case "+str(value)+"; choose 32, 76 or 97")
    return _ALIASES[key]


def select_support_case(data, topology, case=None, *, wall_base_extension=None):
    """Return reviewed support case without modifying the exported model.

    [REF components/model/assembly.py _gravity_wall_support_strategy]
    Physical 32 is project-specific: missing tags or invalid restraints
    block this choice rather than inventing fixed DOFs. The diagnostic
    97 case requires the existing geometry-driven wall-edge extension.
    """
    profile=normalize_support_case(case)
    if not isinstance(data,dict) or not isinstance(data.get("supports"),dict):
        raise ValueError("Source exported restraint mapping is required")
    original={str(tag): list(flags) for tag,flags in data["supports"].items()}
    primary={str(n) for n in PROJECT_PRIMARY_32}
    if len(primary)!=32:
        raise RuntimeError("Invalid 32 physical foundation tag contract")
    missing=sorted(primary-original.keys(), key=int)
    if missing:
        raise ValueError("Missing user-confirmed 32 physical foundation tags: "+",".join(missing))
    for tag,flags in original.items():
        if len(flags)!=6 or any(type(v) not in (int,bool) or v not in (0,1,False,True) for v in flags):
            raise ValueError("Invalid six-DOF source restraint at tag "+tag)
    selected={}; added=[]
    if profile=="PHYSICAL_32":
        for tag in sorted(primary,key=int):
            if not original[tag][2]:
                raise ValueError("User-confirmed physical support has no native vertical restraint: "+tag)
            selected[tag]=original[tag]
        purpose="PRIMARY_32_PHYSICAL_FOUNDATIONS_NATIVE_EDGE_TRANSFER_UNVERIFIED"
    elif profile=="SOURCE_76":
        if len(original)!=76:
            raise ValueError("76 source diagnostic requires exactly 76 original restrained tags")
        selected=original
        purpose="DIAGNOSTIC_76_SOURCE_RESTRAINTS_NOT_76_PHYSICAL_FOUNDATIONS"
    else:
        if len(original)!=76 or wall_base_extension is None:
            raise ValueError("97 diagnostic requires 76 source tags, native wall topology and explicit wall-base extension")
        selected,added=wall_base_extension(
            data,topology,"CONTINUOUS_WALL_BASE_FIXED")
        selected={str(tag):list(flags) for tag,flags in selected.items()}
        if len(selected)!=97 or len(added)!=21:
            raise ValueError("97 extension must create exactly 21 geometric wall-base restraint points")
        purpose="DIAGNOSTIC_97_ADDED_FIXED_WALL_BASE_IDEALIZATION"
    excluded=sorted(set(original)-set(selected),key=int)
    return dict(
        profile=profile, supports=selected, added_wall_mesh_support_tags=added,
        excluded_mesh_point_tags=[int(t) for t in excluded],
        source_restraint_count=len(original),
        user_confirmed_physical_foundation_count=32,
        selected_restraint_count=len(selected),
        engineering_acceptance="NOT_VERIFIED",
        native_wall_edge_mpc_transfer="NOT_VERIFIED",
        purpose=purpose,
    )
