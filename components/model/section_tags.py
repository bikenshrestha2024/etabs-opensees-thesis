"""Nonlinear frame section tag registry and ETABS section-name validation.

[REF OpenSees 'section Fiber' / 'beamIntegration' manual (integer tag namespaces)]
[REF R10 NBC105-2025 §9.3.1 (3D nonlinear model must represent the as-modelled members)]

Replaces the literal ``{'SHS_350x350x16_STEEL_FIBER':701, ...}`` that was
repeated in components/model/assembly.py and components/ui/application.py.

* Default tags come from ``components.sections.definitions.SECTION_TAGS`` —
  the same module that actually creates those fibre sections, so the numbers
  cannot drift apart.
* ``nonlinear_section_tags`` in OpenSees_Complete_Model_Config_V118.json may
  add or change tags ONLY for the reviewed (non-research) route, where the
  project's own ``nonlinear_materials_file`` defines the sections. The research
  route always calls ``define_all_fiber_sections``, so an override there must
  equal the defined tags or it is rejected.
* ``validate_frame_mapping`` checks, before any element is created, that every
  ETABS frame section name that will become a forceBeamColumn has a
  ``frame_section_mapping`` entry whose target has a registered tag.
With no override the resolved tags are identical to the previous literal.
"""
from __future__ import annotations

# ShellMITC4 ElasticMembranePlateSection tags start at 500000 in assembly.py.
SHELL_SECTION_TAG_BASE = 500000


def default_section_tags():
    """Return a copy of the fibre-section tags created by definitions.py.

    [REF components/sections/definitions.py SECTION_TAGS] single source.
    """
    from components.sections.definitions import SECTION_TAGS
    return dict(SECTION_TAGS)


def resolve_nonlinear_section_tags(cfg, *, research=False):
    """Merge and validate ``cfg['nonlinear_section_tags']`` over the defaults.

    [REF OpenSees section tag namespace] tags must be unique positive integers
    below SHELL_SECTION_TAG_BASE (shell sections are numbered from there).
    Inputs: model config mapping; ``research`` True when sections are created
    by define_all_fiber_sections (fixed tags).
    Output: dict {target section name: int tag}. Raises ValueError.
    """
    tags = default_section_tags()
    override = cfg.get('nonlinear_section_tags') or {}
    if not isinstance(override, dict):
        raise ValueError('nonlinear_section_tags must be an object {section_name: tag}')
    for name, tag in override.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError('nonlinear_section_tags keys must be section names')
        if isinstance(tag, bool) or not isinstance(tag, int) or tag <= 0:
            raise ValueError(f'nonlinear_section_tags[{name!r}] must be a positive integer')
        if tag >= SHELL_SECTION_TAG_BASE:
            raise ValueError(f'nonlinear_section_tags[{name!r}]={tag} collides with shell '
                             f'section tags (>= {SHELL_SECTION_TAG_BASE})')
        if research and name in tags and tags[name] != tag:
            raise ValueError(f'Research profile defines {name} with tag {tags[name]}; '
                             f'override {tag} would reference an undefined section')
        if research and name not in tags:
            raise ValueError(f'Research profile cannot use section {name!r}: it is not '
                             'created by define_all_fiber_sections')
        tags[name] = tag
    seen = {}
    for name, tag in tags.items():
        if tag in seen:
            raise ValueError(f'Duplicate section tag {tag}: {seen[tag]} and {name}')
        seen[tag] = name
    return tags


def validate_frame_mapping(data, cfg, section_tags, *, overrides=None, research=False):
    """Check ETABS frame section names against mapping and registered tags.

    [REF R10 NBC105-2025 §9.3.1] every modelled member needs a defined
    nonlinear representation; fail before building any element.
    Mirrors build_complete_model: device-target frames and research hinged
    braces (corotTruss) do not use a fibre section.
    Output: dict(used_targets=..., unused_mapping_keys=...). Raises ValueError
    listing ALL unmapped ETABS section names / unknown targets.
    """
    overrides = overrides or {}
    mapping = cfg.get('frame_section_mapping') or {}
    unmapped, unknown, used = set(), set(), set()
    etabs_names = set()
    for i, e in enumerate(data.get('frames', [])):
        tag = 100001 + i
        name = e['properties'].get('section')
        etabs_names.add(name)
        selection = overrides.get('SOLVER:' + str(tag), overrides.get('FRAME:' + str(e['object']), {}))
        if selection.get('target') in ('FVD_MAXWELL', 'BRB_STEEL02'):
            continue
        if e.get('hinged_brace') and research:
            continue
        if e.get('hinged_brace'):
            continue  # build_complete_model raises its own specific error
        target = selection.get('target') or mapping.get(name)
        if target is None:
            unmapped.add(str(name))
        elif target not in section_tags:
            unknown.add(f'{name} -> {target}')
        else:
            used.add(target)
    if unmapped or unknown:
        parts = []
        if unmapped:
            parts.append('ETABS sections without frame_section_mapping: ' + ', '.join(sorted(unmapped)))
        if unknown:
            parts.append('mapping targets without a registered nonlinear section tag: '
                         + ', '.join(sorted(unknown)))
        raise ValueError('; '.join(parts))
    return dict(used_targets=sorted(used),
                unused_mapping_keys=sorted(k for k in mapping if k not in etabs_names))
