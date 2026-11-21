"""Named opt-in configuration presets for ETABS-vs-OpenSees elastic comparisons.

``ETABS_ELASTIC_GRAVITY_COMPARISON`` turns on, together:

* native ETABS frame and shell stiffness modifiers (``Wall 600`` f11 = f22 = f12 = 0.5,
  m = 0.1; beams I 0.35 and J 0.01; columns I 0.7), via ``elastic_etabs_comparison``;
* the reviewed thin-shell transverse-shear approximation needed for m = 0.1 with v = 1;
* ETABS rigid end zones from the assignment workbook (``rigid_end_zones``);
* the verified clear-length beam self-weight policy, which must already be set and
  confirmed by ``tools/REBUILD_VERIFIED_CLEAR_BEAM_MODEL.py`` (the preset never sets
  the confirmation flag itself).

Not included: ``wall_max_cell_size_m``. Every wall has ``Area Assigns - Wall Auto Mesh``
= ``Default``, and for a straight wall ETABS "Default" means the object is not meshed
(CSI help, Assign > Shell > Wall Auto Mesh Options); the 1 m ``Analysis - Wall Mesh
Settings`` value applies only to walls that use auto rectangular meshing. The historical
OpenSees wall mesh (lines from slab and opening geometry only) is the closest available
representation.

Frames stay Euler-Bernoulli (no ``shear_flexible_sections``): OpenSees
``ElasticTimoshenkoBeam`` with ``-jntOffset`` is not qualified in this repository
(``compile_settings`` rejects the combination).

The preset is diagnostic. Production defaults are not changed.

[REF docs/source/components/model/etabs_comparison_preset.py.md]
"""
from __future__ import annotations

import copy

ETABS_ELASTIC_GRAVITY_COMPARISON = "ETABS_ELASTIC_GRAVITY_COMPARISON"

PRESETS = {
    ETABS_ELASTIC_GRAVITY_COMPARISON: {
        "elastic_etabs_comparison": {
            "ULS": {
                "use_native_frame_modifiers": True,
                "use_native_shell_modifiers": True,
                "allow_shell_shear_approximation": True,
            }
        },
        "rigid_end_zones": {"enabled": True, "source": "ASSIGNMENT_WORKBOOK", "factor": "SOURCE"},
    }
}
# Run-time comparison procedure that goes with the preset (not a model config key).
# ETABS evidence: every wall is Wall Auto Mesh = Default (straight walls are not
# meshed, so a wall base edge is a single shell edge between its two restrained
# corner joints) and the 44 restrained ETABS base points that lie inside those edges
# report FZ = 0 in "1. DL + LL" (they are not connected to the unmeshed walls).
# OpenSees therefore fixes every wall-base mesh node on such an edge
# (gravity strategy CONTINUOUS_WALL_BASE_FIXED) and lumps each intermediate reaction
# onto the two corner supports with the linear edge weights (1 - t, t)
# (tools/etabs_comparison_ablation.lump_to_reference_supports).
COMPARISON_PROCEDURE = {
    ETABS_ELASTIC_GRAVITY_COMPARISON: {
        "gravity_support_strategy": "CONTINUOUS_WALL_BASE_FIXED",
        "reaction_comparison": "LUMP_WALL_BASE_NODES_TO_ETABS_CORNER_SUPPORTS_LINEAR_EDGE",
    }
}
REQUIRED_EXISTING = {
    ETABS_ELASTIC_GRAVITY_COMPARISON: {
        "etabs_beam_weight_policy": "ETABS_BEAM_CLEAR_LENGTH",
        "etabs_clear_beam_weight_confirmed": True,
    }
}


def preset_settings(name):
    """Return a deep copy of the config keys a preset sets.

    [REF docs/source/components/model/etabs_comparison_preset.py.md]
    """
    if name not in PRESETS:
        raise ValueError("Unknown comparison preset " + repr(name) + "; known: " + ", ".join(PRESETS))
    return copy.deepcopy(PRESETS[name])


def apply_preset(config, name):
    """Return a copy of ``config`` with the preset keys set; refuse conflicting existing keys.

    [REF engineering/rules/CORE_RULES.md rule 5] no silent stiffness/weight change: the
    clear-beam weight policy must already be confirmed, and existing different values
    for a preset key raise instead of being overwritten.
    """
    if not isinstance(config, dict):
        raise ValueError("Model config must be a JSON object")
    for key, value in REQUIRED_EXISTING.get(name, {}).items():
        if config.get(key) != value:
            raise ValueError(f"Preset {name} requires {key} = {value!r} (verified clear-beam rebuild)")
    result = copy.deepcopy(config)
    for key, value in preset_settings(name).items():
        if key in result and result[key] not in (None, value):
            raise ValueError(f"Preset {name}: config already sets {key} differently; remove it first")
        result[key] = value
    result["comparison_preset"] = name
    return result
