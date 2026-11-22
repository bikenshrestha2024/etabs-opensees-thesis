"""Shared repository-root resolution for direct modules and exec-loaded facades.

[REF docs/source/components/shared/repository_paths.py.md]
A root-level compatibility facade records its actual component path in
_component_source. Never derive a project root from CWD or a selected output.
"""
from __future__ import annotations
from pathlib import Path


def runtime_repo_root(module_file, component_source=None):
    """[REF docs/source/components/shared/repository_paths.py.md]
    Preserve source-root semantics for imported and exported project copies.

    This helper is deliberately independent of the ETABS/OpenSees engines.
    Each compat facade must pass its actual _component_source explicitly;
    a newly selected GUI folder never influences code import ownership.
    """
    source=component_source or module_file
    return Path(source).resolve().parents[2]
