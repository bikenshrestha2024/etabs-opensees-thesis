"""Resolve elastic ETABS comparison inputs in kN–m before generating the model."""
from collections import defaultdict
import json
import math
from pathlib import Path

from components.model.linear_shell_stiffness import FIELDS, positive, shell_section_parameters
from components.model.physical_weight_modifiers import FRAME_LABELS


FRAME_FIELDS = FRAME_LABELS[:6]
FRAME_PROPERTY = {"A": "A", "As2": "As2", "As3": "As3", "J": "J", "I22": "Iy", "I33": "Iz"}
OPTION_KEYS = {
    "frame_sections", "frame_objects", "shell_sections", "shell_objects", "end_offsets_m",
    "use_native_frame_modifiers", "use_native_shell_modifiers", "shear_flexible_sections",
    "allow_shell_shear_approximation",
}


def default_frame_bending(frame, state):
    """Apply the legacy limit-state bending factors to unoverridden axes.

    [REF engineering/rules/CORE_RULES.md rule 5] stiffness changes must not be silent; the factor values
    are legacy project defaults with no code clause verified here (clause to be verified).
    """
    if frame["properties"]["E"] > 1e8:
        return 1.
    if frame["category"] == "COLUMN":
        return .9 if state == "SLS" else .7
    return .7 if state == "SLS" else .35


def _check_keys(mapping, allowed, label):
    if not isinstance(mapping, dict):
        raise ValueError(f"{label} must be a JSON object")
    extra = set(mapping) - set(allowed)
    if extra:
        raise ValueError(f"{label} has unknown keys: {', '.join(sorted(extra))}")


def read_comparison_settings(filename):
    """[REF docs/source/components/model/elastic_conversion_settings.py.md] Read explicit ULS/SLS settings."""
    file = Path(filename).expanduser()
    if file.suffix.casefold() != '.json' or file.name.casefold().endswith('.processing.json'):
        raise ValueError('Select the ULS/SLS elastic settings JSON. Processing sidecars only record timing.')
    settings = json.loads(file.read_text(encoding='utf-8-sig'))
    _check_keys(settings, ('ULS','SLS'), 'Elastic comparison settings')
    if not settings:
        raise ValueError('Elastic comparison settings must specify ULS or SLS.')
    for state, options in settings.items():
        _check_keys(options, OPTION_KEYS, state)
        if not options:
            raise ValueError(f'{state} elastic comparison settings are empty.')
    return settings


def _native_factors(records, kind, object_id, section, fields):
    source = records.get((kind, object_id), {})
    section_factors = source.get("section_modifiers") or {}
    object_factors = source.get("object_modifiers") or {}
    if source.get("section") != section or any(key not in values
            for key in (*fields, "mass", "weight")
            for values in (section_factors, object_factors)):
        raise ValueError(f"Incomplete native ETABS {kind} modifiers for {object_id} / {section}")
    for factors in (section_factors, object_factors):
        for key in ("mass", "weight"):
            if not math.isclose(float(factors[key]), 1., rel_tol=0., abs_tol=1e-9):
                raise ValueError(f"ETABS {kind} {object_id}: reconcile native {key} separately")
    return {key: positive(section_factors[key], key) * positive(object_factors[key], key)
            for key in fields}


def _overrides(factors, sections, objects, section, obj):
    for label, mapping in ((section, sections.get(section, {})), (obj, objects.get(obj, {}))):
        _check_keys(mapping, factors, f"stiffness modifiers {label}")
        factors.update({key: positive(value, f"{label} {key}") for key, value in mapping.items()})
    return factors


def _offsets(offsets, frames):
    """Convert reviewed ETABS effective end lengths into global offsets on outer segments."""
    groups = defaultdict(list)
    for index, frame in enumerate(frames):
        groups[str(frame["object"])].append(index)
    result = {}
    for obj, entry in offsets.items():
        _check_keys(entry, ("i", "j", "rigid_fraction"), f"frame {obj} offset")
        if set(entry) != {"i", "j", "rigid_fraction"}:
            raise ValueError(f"frame {obj} offset needs i, j and rigid_fraction")
        li, lj, rigid = (float(entry[key]) for key in ("i", "j", "rigid_fraction"))
        indices = sorted(groups[obj], key=lambda i: frames[i]["start"])
        first, last = indices[0], indices[-1]
        if not all(math.isfinite(x) and x >= 0. for x in (li, lj, rigid)) or rigid > 1.:
            raise ValueError(f"invalid end lengths or rigid fraction for frame {obj}")
        if li + lj >= frames[last]["end"] - frames[first]["start"]:
            raise ValueError(f"end offsets exhaust frame {obj} clear length")
        i_offset, j_offset = li * rigid, lj * rigid
        if first == last:
            if i_offset or j_offset:
                result[first] = i_offset, j_offset
        else:
            if i_offset:
                result[first] = i_offset, 0.
            if j_offset:
                result[last] = 0., j_offset
    return result



def audit_native_end_offset_coverage(options, frames, metadata):
    """Compare ETABS *source* rigid end-zone assignments with explicit inputs.

    Diagnostic only. Does NOT apply an offset, recalibrate a support reaction,
    or certify that the OpenSees element reproduces ETABS rigid-zone stiffness.
    [REF docs/source/components/model/elastic_conversion_settings.py.md]
    """
    frame_lookup = {}
    for frame in frames:
        obj = str(frame["object"])
        section = str(frame["properties"]["section"])
        if obj in frame_lookup and frame_lookup[obj] != section:
            raise ValueError("Conflicting section assignments across segments of frame " + obj)
        frame_lookup[obj] = section
    source_frames = (metadata or {}).get("frames") or {}
    supplied = options.get("end_offsets_m", {})
    shear_sections = set(options.get("shear_flexible_sections", []))
    missing_source = []
    unmodeled = []
    conflicting = []
    matched = []
    native_active = 0
    native_shear_active = 0
    native_active_by_section = defaultdict(int)
    for obj, section in sorted(frame_lookup.items()):
        row = source_frames.get(obj) or {}
        raw = row.get("GetEndLengthOffset")
        if not isinstance(raw, (list, tuple)) or len(raw) != 5 or raw[-1] != 0:
            missing_source.append(obj)
            continue
        try:
            i_length, j_length, rigid = map(float, raw[1:4])
        except (TypeError, ValueError):
            missing_source.append(obj)
            continue
        if not all(math.isfinite(value) for value in (i_length, j_length, rigid)):
            missing_source.append(obj)
            continue
        if min(i_length, j_length, rigid) < 0 or rigid > 1:
            missing_source.append(obj)
            continue
        if (i_length + j_length) * rigid <= 1e-9:
            continue
        native_active += 1
        native_active_by_section[section] += 1
        if section in shear_sections:
            native_shear_active += 1
        values = supplied.get(obj)
        if values is None:
            unmodeled.append(obj)
            continue
        try:
            same = all(math.isclose(float(values[key]), expected, rel_tol=0., abs_tol=1e-8)
                       for key, expected in (("i", i_length), ("j", j_length),
                                             ("rigid_fraction", rigid)))
        except (TypeError, ValueError, KeyError):
            same = False
        (matched if same else conflicting).append(obj)
    if not frame_lookup:
        status = "NO_ASSEMBLED_FRAME_OBJECTS"
    elif len(missing_source) == len(frame_lookup):
        status = "NATIVE_RIGID_ZONE_SOURCE_METADATA_UNAVAILABLE"
    elif missing_source or unmodeled or conflicting:
        status = "NATIVE_RIGID_ZONE_COVERAGE_INCOMPLETE"
    else:
        status = "NATIVE_RIGID_ZONE_INPUTS_MATCH_SOURCE_NOT_SOLVER_VALIDATION"
    return dict(
        status=status,
        assembled_unique_frame_objects=len(frame_lookup),
        native_offset_metadata_available_count=len(frame_lookup)-len(missing_source),
        native_active_rigid_zone_objects=native_active,
        native_active_rigid_zone_by_section=dict(sorted(native_active_by_section.items())),
        native_rigid_zone_on_selected_shear_flexible_objects=native_shear_active,
        native_offsets_configured_exact_count=len(matched),
        native_offsets_unmodeled_count=len(unmodeled),
        native_offsets_differ_from_source_count=len(conflicting),
        native_offset_metadata_missing_count=len(missing_source),
        unmodeled_object_ids_sample=unmodeled[:12],
        conflicting_object_ids_sample=conflicting[:12],
        missing_source_object_ids_sample=missing_source[:12],
        engineering_acceptance="NOT_VERIFIED",
        warning=(
            "An ETABS-elastic modifier match is not an end-zone stiffness match. "
            "Native ETABS rigid offsets with no reviewed end_offsets_m remain "
            "unmodeled. The current ElasticTimoshenkoBeam adapter explicitly "
            "rejects combining shear-flexible elements and nonzero joint offsets; "
            "isolate, validate, and document a compatible formulation before "
            "changing production stiffness or declaring ETABS reaction equivalence."
        ),
    )


def compile_settings(config, frames, shells, metadata):
    """Bind state-specific settings to the actual frame segments and shell objects.

    [REF engineering/rules/CORE_RULES.md rule 5] explicit, key-checked settings instead of silent stiffness/unit changes.
    """
    _check_keys(config, ("ULS", "SLS"), "elastic_etabs_comparison")
    frame_ids = {str(e["object"]) for e in frames}
    frame_sections = {e["properties"]["section"] for e in frames}
    shell_ids = {str(e["object"]) for e in shells}
    shell_sections = {e["properties"]["property"] for e in shells}
    records = {(r["kind"], str(r["object"])): r
               for r in metadata.get("etabs_property_modifiers", {}).get("records", [])}
    result = {}
    for state, options in config.items():
        _check_keys(options, OPTION_KEYS, state)
        for key, allowed in (("frame_sections", frame_sections), ("frame_objects", frame_ids),
                             ("shell_sections", shell_sections), ("shell_objects", shell_ids),
                             ("end_offsets_m", frame_ids)):
            _check_keys(options.get(key, {}), allowed, f"{state} {key}")
        for flag in ("use_native_frame_modifiers", "use_native_shell_modifiers",
                     "allow_shell_shear_approximation"):
            if type(options.get(flag, False)) is not bool:
                raise ValueError(f"{state} {flag} must be boolean")
        shear = options.get("shear_flexible_sections", [])
        if not isinstance(shear, list) or any(not isinstance(k, str) or k not in frame_sections for k in shear):
            raise ValueError(f"{state} shear_flexible_sections must list assembled section names")
        offset_coverage = audit_native_end_offset_coverage(options, frames, metadata)
        offsets = _offsets(options.get("end_offsets_m", {}), frames)
        segments = []
        for index, frame in enumerate(frames):
            p = frame["properties"]
            obj, section = str(frame["object"]), p["section"]
            rigid_i, rigid_j = offsets.get(index, (0., 0.))
            retained = 1. - (rigid_i + rigid_j) / frame["length"]
            if retained <= 1e-9:
                raise ValueError(f"frame {obj}: rigid offset reaches beyond its outer segment")
            use_shear = section in shear and not frame.get("hinged_brace")
            if use_shear and (frame.get("release_i") or frame.get("release_j")):
                raise ValueError(f"frame {obj}: the shear-flexible element cannot preserve end releases")
            if use_shear and retained < 1.:
                raise ValueError(f"frame {obj}: combined Timoshenko and joint offsets require qualification")
            native = options.get("use_native_frame_modifiers", False)
            factors = (_native_factors(records, "frame", obj, section, FRAME_FIELDS) if native
                       else dict.fromkeys(FRAME_FIELDS, 1.))
            if not native:
                factors.update(I22=default_frame_bending(frame, state),
                               I33=default_frame_bending(frame, state))
            factors = _overrides(factors, options.get("frame_sections", {}),
                                 options.get("frame_objects", {}), section, obj)
            if not use_shear and (factors["As2"] != 1. or factors["As3"] != 1.):
                raise ValueError(f"frame {obj}: nonunity As2/As3 requires a shear-flexible section")
            properties = {prop: p[prop]*factors[key] for key, prop in FRAME_PROPERTY.items()
                          if prop in p}
            if use_shear:
                for field in ("As2", "As3"):
                    positive(properties.get(field), f"frame {obj} {field} in m²")
            # Keep the full-length axial and torsional compliance while shortening
            # the flexible bending span. Weight and mass use the original member.
            properties["A"] *= retained
            properties["J"] *= retained
            axis = frame["basis"][0]
            segments.append(dict(properties=properties, modifiers=factors, shear_flexible=use_shear,
                                 joint_offsets_m=[*(rigid_i*v for v in axis),
                                                  *(-rigid_j*v for v in axis)]))
        shell_plan = {}
        native = options.get("use_native_shell_modifiers", False)
        for element in shells:
            p = element["properties"]
            obj, section = str(element["object"]), p["property"]
            by_section, by_object = options.get("shell_sections", {}), options.get("shell_objects", {})
            if obj in shell_plan or not (native or section in by_section or obj in by_object):
                continue
            factors = dict.fromkeys(FIELDS, 1.)
            if element["category"] == "FLOOR":
                plate = .35 if state == "SLS" else .25
                factors.update(m11=plate, m22=plate, m12=plate, v13=plate, v23=plate)
            if native:
                factors.update(_native_factors(records, "area", obj, section, FIELDS[:8]))
            factors = _overrides(factors, by_section, by_object, section, obj)
            approximate = options.get("allow_shell_shear_approximation", False)
            shell_plan[obj] = shell_section_parameters(
                p["E"], p["nu"], p["thickness"], factors, property_name=section,
                source_kind="ETABS_MODIFIERS_WITH_EXPLICIT_ELASTIC_OVERRIDES",
                transverse_shear_policy=("ALLOW_REVIEWED_THIN_SHELL_APPROX" if approximate
                                         else "REJECT_DIFFERENCE"))
        result[state] = dict(frame_segments=segments, shell_objects=shell_plan,
                             native_end_offset_coverage=offset_coverage)
    return result
