"""Inherent (Rayleigh) damping applied only to structural elements and nodal mass.

[REF NBC105-2025 §8.1.1 (as cited in this repository; verify clause text in the DUDBC copy)]
[REF Charney 2008, doi:10.1061/(ASCE)0733-9445(2008)134:4(581)]
[REF Zareian & Medina 2010, Comput. Struct. 88(1-2):45-53]
[REF PEER TBI 2017; LATBSDC 2020 (about 2.5% inherent damping in tall-building practice; section numbers to be verified)]

Why region-based damping
------------------------
``ops.rayleigh(aM, 0, 0, bK)`` assigns the factors to EVERY element and node in
the domain. Stiffness-proportional damping on discrete energy-dissipation
devices (FVD links, BRB / brace trusses) double-counts damping the device
already models explicitly, and on very stiff links creates spurious forces
(Charney 2008). This module assigns:

* region ``REGION_STRUCTURAL``: frame, core-wall and slab elements
  -> ``-rayleigh aM 0 0 bK`` (the mesh region also carries aM to their nodes);
* region ``REGION_MASS_NODES``: ONLY lumped-mass nodes that belong to no
  structural element (e.g. rigid-diaphragm masters) -> ``-rayleigh aM 0 0 0``,
  so they keep the same mass-proportional term as the global command.

Caution (verified natively, OpenSeesPy 3.8.0): ``region -node`` ALSO captures
every element whose nodes all lie in the node set and resets that element's
factors to the region values. A node region containing slab/beam nodes would
therefore silently erase their bK. That is why the node region is restricted
to orphan mass nodes, and why ``-ele`` and ``-node`` are never combined in one
region (OpenSees then ignores the node list).

Device and truss elements are never put in a Rayleigh region.

Native facts checked with OpenSeesPy 3.8.0 (tests/verify_damping_regions.py):
``Truss``/``CorotTruss``/``TwoNodeLink`` ignore stiffness-proportional Rayleigh
damping unless created with ``-doRayleigh 1``. The previous global command
therefore did NOT double-count on the current corotTruss braces / FVD
twoNodeLinks; the region form makes that exclusion explicit and robust to a
future ``-doRayleigh 1`` or a device modelled with a beam element.

Units: aM in 1/s, bK in s (kN-m-s model).
"""
from __future__ import annotations

import math

# [REF PEER TBI 2017; LATBSDC 2020] typical inherent damping for tall
# buildings when supplemental devices and hysteresis are modelled explicitly.
DEFAULT_INHERENT_DAMPING_RATIO = 0.025
# [REF NBC105-2025 §8.1.1 (repo citation)] upper bound on linear viscous damping.
NBC105_FIVE_PERCENT = 0.05

REGION_STRUCTURAL = 9101
REGION_MASS_NODES = 9102

# OpenSees class names (ops.eleType) that are discrete devices or axial members.
# [REF OpenSees TwoNodeLink / Truss / CorotTruss manual: '-doRayleigh' flag]
EXCLUDED_ELEMENT_TYPES = frozenset({
    'TwoNodeLink', 'ZeroLength', 'ZeroLengthSection', 'ZeroLengthND',
    'Truss', 'CorotTruss', 'TrussSection', 'CorotTrussSection',
    'ViscousDamper', 'ElastomericBearingBoucWen3d', 'FlatSliderSimple3d',
})


def resolve_inherent_damping_ratio(config):
    """Return the inherent damping ratio selected by explicit configuration.

    [REF PEER TBI 2017; LATBSDC 2020] default 0.025.
    [REF NBC105-2025 §8.1.1 (repo citation)] 5% only with
    ``inherent_damping_five_percent: true``; ratios above 2.5% require that flag.

    Inputs: config mapping with optional ``inherent_damping_ratio`` (fraction,
    not percent) and boolean ``inherent_damping_five_percent``.
    Output: float ratio in (0, 0.05]. Raises ValueError for anything else.
    """
    five = config.get('inherent_damping_five_percent', False)
    if not isinstance(five, bool):
        raise ValueError('inherent_damping_five_percent must be true or false')
    raw = config.get('inherent_damping_ratio')
    if raw is None:
        return NBC105_FIVE_PERCENT if five else DEFAULT_INHERENT_DAMPING_RATIO
    if isinstance(raw, bool):
        raise ValueError('inherent_damping_ratio must be a number (fraction, e.g. 0.025)')
    zeta = float(raw)
    if not math.isfinite(zeta) or not 0 < zeta <= NBC105_FIVE_PERCENT:
        raise ValueError('inherent_damping_ratio must be in (0, 0.05]; it is a fraction, not percent')
    if zeta > DEFAULT_INHERENT_DAMPING_RATIO + 1e-12 and not five:
        raise ValueError('inherent_damping_ratio above 0.025 requires '
                         'inherent_damping_five_percent=true (explicit opt-in)')
    return zeta


def classify_elements(ops, element_tags=None, *, extra_excluded_tags=()):
    """Split element tags into Rayleigh-damped structural and excluded devices.

    [REF Charney 2008; Zareian & Medina 2010] exclude discrete devices/links.
    Uses ``ops.eleType`` (OpenSeesPy >= 3.4). Unknown element types are kept
    structural, so a NEW device class must be added to EXCLUDED_ELEMENT_TYPES
    or listed in ``extra_excluded_tags``.

    Output: dict(structural=[tags], excluded=[tags], types={type: count},
    excluded_types={type: count}).
    """
    tags = [int(t) for t in (ops.getEleTags() if element_tags is None else element_tags)]
    extra = {int(t) for t in extra_excluded_tags}
    structural, excluded, types, excluded_types = [], [], {}, {}
    for tag in tags:
        kind = str(ops.eleType(tag))
        types[kind] = types.get(kind, 0) + 1
        if tag in extra or kind in EXCLUDED_ELEMENT_TYPES:
            excluded.append(tag)
            excluded_types[kind] = excluded_types.get(kind, 0) + 1
        else:
            structural.append(tag)
    return dict(structural=structural, excluded=excluded, types=types,
                excluded_types=excluded_types)


def mass_node_tags(ops):
    """Return node tags carrying any nonzero lumped translational/rotational mass.

    [REF OpenSees 'nodeMass' command] mass-proportional Rayleigh term acts on
    nodal mass; these nodes receive aM in REGION_MASS_NODES.
    """
    out = []
    for node in ops.getNodeTags():
        ndf = len(ops.nodeDisp(node))
        if any(abs(float(ops.nodeMass(node, d + 1))) > 0 for d in range(ndf)):
            out.append(int(node))
    return out


def apply_structural_rayleigh(ops, alpha_m, beta_k, *, extra_excluded_tags=()):
    """Assign Rayleigh damping to structural elements and mass nodes only.

    [REF NBC105-2025 §8.1.1 (repo citation); Charney 2008; OpenSees 'region']
    Committed-stiffness form (bK -> betaKcomm, 4th rayleigh argument), as in
    the previous global ``ops.rayleigh(aM, 0, 0, bK)`` call.

    Side effect: defines regions REGION_STRUCTURAL and REGION_MASS_NODES.
    Output: audit dict (JSON-serialisable) for the case folder.
    """
    alpha_m, beta_k = float(alpha_m), float(beta_k)
    if not (math.isfinite(alpha_m) and math.isfinite(beta_k)) or alpha_m < 0 or beta_k < 0:
        raise ValueError('Rayleigh coefficients must be finite and non-negative')
    groups = classify_elements(ops, extra_excluded_tags=extra_excluded_tags)
    structural_nodes = {int(n) for tag in groups['structural'] for n in ops.eleNodes(tag)}
    # Orphan mass nodes only: see module caution on region -node element capture.
    nodes = [n for n in mass_node_tags(ops) if n not in structural_nodes]
    if groups['structural']:
        ops.region(REGION_STRUCTURAL, '-ele', *groups['structural'],
                   '-rayleigh', alpha_m, 0., 0., beta_k)
    if nodes:
        ops.region(REGION_MASS_NODES, '-node', *nodes, '-rayleigh', alpha_m, 0., 0., 0.)
    return dict(
        method='region_rayleigh_structural_only',
        alphaM_per_s=alpha_m, betaKcomm_s=beta_k,
        structural_element_count=len(groups['structural']),
        excluded_element_count=len(groups['excluded']),
        excluded_element_tags=groups['excluded'],
        element_types=groups['types'], excluded_element_types=groups['excluded_types'],
        orphan_mass_node_count=len(nodes), orphan_mass_node_tags=nodes,
        regions=dict(structural=REGION_STRUCTURAL, mass_nodes=REGION_MASS_NODES),
        reference='[REF Charney 2008; Zareian & Medina 2010; NBC105-2025 §8.1.1 (repo citation)]',
    )


def modal_damping_ratios(alpha_m, beta_k, eigenvalues):
    """Initial-stiffness Rayleigh ratio per mode: aM/(2w) + bK*w/2.

    [REF Chopra, Dynamics of Structures, Ch. 11 (Rayleigh damping)] Output: list of fractions.
    """
    return [alpha_m / (2 * math.sqrt(v)) + beta_k * math.sqrt(v) / 2
            for v in eigenvalues if v > 0]
