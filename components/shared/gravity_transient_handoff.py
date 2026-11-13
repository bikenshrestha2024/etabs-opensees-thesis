"""NBC 105:2025 §8.1.1.2/§9.3.1.2 gravity-to-transient handoff.

OpenSees: loadConst('-time',0.0) fixes *currently defined* load patterns at
their converged values and resets domain time. It DOES NOT perform gravity,
certify the source weight ledger, remove existing static EL patterns, switch
element transformations, or verify geometric nonlinearity. Call only after the
selected model builder has already converged gravity. A separate analysis
setup must call wipeAnalysis() before transient; never wipe() here.

Sources:
NBC 105:2025 §§5.2, 8.1.1.2–8.1.1.3, 9.3.1.2–9.3.1.3
https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf
OpenSees https://opensees.github.io/OpenSeesDocumentation/user/manual/misc/loadConst.html
Review: REVIEW_MAIN/00_MODEL/20261113_NBC_IS_INITIAL_PDELTA_CODE_HIERARCHY.md
"""
from __future__ import annotations

import math
from typing import Any


def freeze_verified_gravity(ops: Any, *, case: str, builder_gravity_converged: bool) -> dict:
    """Freeze an ALREADY-converged model-builder gravity state before excitation.

    Parameters
    ----------
    ops : live OpenSeesPy domain command object
        No new or removed loads are created here.
    case : str
        Unique case/orientation identifier for provenance.
    builder_gravity_converged : bool
        Must be evidence from a checked model-builder run, not merely 'a model
        script returned'. Callers must not hard-code True without verifying
        native gravity convergence and adopted load-case source/provenance.

    Returns
    -------
    dict
        Minimal handoff state. This is not a numerical equivalence certificate.
    """
    if builder_gravity_converged is not True:
        raise RuntimeError(
            f"{case}: gravity not independently confirmed converged; "
            "refusing to freeze loads for NBC time history."
        )
    nodes = ops.getNodeTags()
    if not nodes:
        raise RuntimeError(f"{case}: OpenSees domain is empty before gravity freeze")
    before = float(ops.getTime())
    if not math.isfinite(before):
        raise RuntimeError(f"{case}: nonfinite pre-freeze domain time {before}")
    ops.loadConst("-time", 0.0)
    after = float(ops.getTime())
    if not math.isfinite(after) or abs(after) > 1e-10:
        raise RuntimeError(f"{case}: loadConst did not reset time to zero ({after})")
    return {
        "case": case,
        "source_standard": "NBC105:2025",
        "gravity_source": "NBC105_5.2_REQUIRES_INDEPENDENT_PROVENANCE",
        "initial_state": "GRAVITY_EQUILIBRIUM_FROZEN",
        "pre_freeze_domain_time": before,
        "post_freeze_domain_time": after,
        "load_patterns_retained": True,
        "static_seismic_el_carried_over": "NOT_INDEPENDENTLY_CHECKED",
        "pdelta_geometry_verified": False,
        "initial_IS16700_EL_case_injected": False,
        "note": (
            "This routine freezes the already-converged gravity patterns only. "
            "It does not copy signed IS initial static EL patterns into TH. "
            "P-Delta geometric transformations and source-load identity require "
            "independent signed-case and model review."
        ),
    }
