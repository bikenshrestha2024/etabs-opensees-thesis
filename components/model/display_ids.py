"""Stable *display-only* labels for ETABS/OpenSees objects.

Engineering display labels must NEVER replace solver integers, ETABS unique IDs,
constraint references, recorder tags, or archived mapping identities.
REF REVIEW_MAIN/00_MODEL/20261114_EXPORT_ID_HINGE_MESH_REVIEW.md
"""
from collections import defaultdict

PREFIXES = {
    "NODE": "N",
    "BEAM": "B",
    "COLUMN": "C",
    "CONVENTIONAL OUTRIGGER": "CO",
    "BELT TRUSS": "BT",
    "CAP TRUSS": "CT",
    "SHEAR WALL": "SW",
    "FLOOR": "FL",
}
# A segment is not automatically an outrigger solely because it is diagonal.
# Source classification is mandatory for CO, BT and CT.


def display_label(prefix, storey, position):
    """Produce labels such as N1, N101, N202, B701, SW2501.

    [REF docs/source/components/model/display_ids.py.md]

    Position is one-based within (category, storey), deterministic upstream.
    Reserve the first 99 slots in each storey for 100-based human labels.
    Additional objects use an unambiguous extended label rather than collide
    with the next floor; the solver tag is never touched.
    """
    if prefix not in PREFIXES.values():
        raise ValueError(f"Unknown display prefix: {prefix}")
    if isinstance(storey, bool) or not isinstance(storey, int) or storey < 0:
        raise ValueError("Storey must be a non-negative integer")
    if isinstance(position, bool) or not isinstance(position, int) or position < 1:
        raise ValueError("Position must be a positive integer")
    if position <= 99:
        return f"{prefix}{storey * 100 + position}"
    return f"{prefix}-S{storey:02d}-{position:04d}"


def build_labels(objects):
    """Map stable native IDs to display names without modifying those IDs.

    [REF docs/source/components/model/display_ids.py.md]

    Each input mapping needs native_id, storey, category. category must be
    externally classified; provenance of ETABS object/source is preserved.
    All native IDs must be unique within the supplied namespace. When an
    element has multiple solver segments, the caller must supply individual
    distinct native IDs and an explicit parent ETABS object ID separately.
    """
    records = list(objects)
    native_ids = [str(r["native_id"]) for r in records]
    if len(native_ids) != len(set(native_ids)):
        raise ValueError("Duplicate native IDs: display aliases must be bijective")
    grouped = defaultdict(list)
    for record in records:
        category = str(record["category"]).upper().strip()
        if category not in PREFIXES:
            raise ValueError(f"Unclassified category: {category}")
        storey = record["storey"]
        if isinstance(storey, bool) or not isinstance(storey, int) or storey < 0:
            raise ValueError("Invalid storey")
        grouped[(category, storey)].append(str(record["native_id"]))
    result = {}
    for (category, storey), ids in sorted(grouped.items()):
        # Numeric native tags sort numerically; other ETABS IDs sort naturally as strings.
        ids.sort(key=lambda x: (0, int(x)) if x.isdecimal() else (1, x))
        for position, native_id in enumerate(ids, 1):
            result[native_id] = display_label(PREFIXES[category], storey, position)
    if len(set(result.values())) != len(result):
        raise AssertionError("Display-label collision")
    return result
