"""Guard the ETABS point-ID -> OpenSees node-tag coordinate contract.

A coincident physical ETABS point pair can carry independent DOFs or a
native MP/edge relation. It must not be silently collapsed to one node tag
by the converter's XYZ lookup. No native ETABS COM or OpenSees calls here.
[REF docs/source/components/model/source_node_identity.py.md]
"""
from __future__ import annotations

from collections import defaultdict
import math


def coordinate_key(xyz, *, decimals=8):
    """Return a finite kN-m-s model XYZ rounded for deterministic mesh matching."""
    if not isinstance(xyz, (list, tuple)) or len(xyz) != 3:
        raise ValueError("ETABS source joint must have three XYZ coordinates")
    values = []
    for number in xyz:
        if isinstance(number, bool):
            raise ValueError("Boolean ETABS joint coordinate is invalid")
        try:
            value = float(number)
        except (ValueError, TypeError) as exc:
            raise ValueError("Non-numeric ETABS source joint coordinate") from exc
        if not math.isfinite(value):
            raise ValueError("Nonfinite ETABS source joint coordinate")
        values.append(round(value, decimals))
    return tuple(values)


def unique_coordinate_lookup(source_nodes):
    """Map XYZ -> tag, rejecting ambiguous distinct source point identities.

    Source points at the same XYZ can be independent or MPC-linked. Without
    native relationship evidence, neither sharing a solver node nor creating
    an automatic rigid/equalDOF relation is safe.
    """
    lookup = {}
    for tag, xyz in source_nodes.items():
        key = coordinate_key(xyz)
        if key in lookup and str(lookup[key]) != str(tag):
            raise ValueError(
                "Ambiguous coincident ETABS source point tags at XYZ "
                + repr(key) + ": " + str(lookup[key]) + " and " + str(tag)
                + "; native joint merge, release and constraint identities "
                  "must be verified before an automatic shell/frame mesh lookup"
            )
        lookup[key] = tag
    return lookup


def audit_node_map_identity(node_map):
    """Read-only evidence audit; never create or erase a source-node relation."""
    if not isinstance(node_map, list):
        return dict(status="SOURCE_NODE_MAP_UNAVAILABLE", records=0,
                    parsed=0, missing_rows=0, duplicate_coordinate_groups=[],
                    duplicate_solver_tags=[], native_constraint_equivalence="NOT_VERIFIED")
    coordinates = defaultdict(list)
    tags = defaultdict(list)
    missing = []
    for index, row in enumerate(node_map):
        if not isinstance(row, dict):
            missing.append(index)
            continue
        tag = row.get("opensees_node_tag")
        xyz = row.get("coordinates_m")
        if tag is None or xyz is None:
            missing.append(index)
            continue
        try:
            key = coordinate_key(xyz)
        except ValueError:
            missing.append(index)
            continue
        name = str(row.get("etabs_point_name", ""))
        coordinates[key].append(dict(opensees_tag=str(tag), etabs_point=name))
        tags[str(tag)].append(dict(coordinates=key, etabs_point=name))
    duplicates = [
        dict(coordinates_m=list(key), identities=rows)
        for key, rows in sorted(coordinates.items())
        if len({v["opensees_tag"] for v in rows}) > 1
    ]
    reused = [
        dict(opensees_tag=tag, identities=rows)
        for tag, rows in sorted(tags.items())
        if len({v["etabs_point"] for v in rows}) > 1
        or len({v["coordinates"] for v in rows}) > 1
    ]
    status = (
        "SOURCE_NODE_MAP_UNAVAILABLE" if not node_map else
        "COINCIDENT_DISTINCT_SOURCE_NODES_REQUIRE_NATIVE_REVIEW" if duplicates else
        "NONUNIQUE_SOURCE_TO_SOLVER_TAGS_REQUIRE_NATIVE_REVIEW" if reused else
        "SOURCE_NODE_COORDINATES_INCOMPLETE" if missing else
        "SOURCE_NODE_IDENTITY_UNIQUE_NOT_NATIVE_VERIFIED"
    )
    return dict(
        status=status,
        records=len(node_map),
        parsed=len(node_map)-len(missing),
        missing_rows=len(missing),
        missing_row_indices_sample=missing[:12],
        duplicate_coordinate_group_count=len(duplicates),
        duplicate_coordinate_groups=duplicates[:20],
        duplicate_solver_tag_count=len(reused),
        duplicate_solver_tags=reused[:20],
        native_constraint_equivalence="NOT_VERIFIED",
        note="Coordinate uniqueness does not prove ETABS shell auto-edge, frame split, diaphragm MPC, support or local-axis equivalence.",
    )
