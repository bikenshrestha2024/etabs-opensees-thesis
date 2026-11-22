"""Resolve static Python module edges; never import or execute project code.

The containing package determines relative-import resolution. Imported names
are treated as submodules only if their .py file or directory exists; normal
symbols such as 'from .solver import run' must not become fake edges.
This is an audit utility, not evidence of runtime execution.
"""
from __future__ import annotations

import ast
from pathlib import Path


def _package_parts(source: str) -> tuple[str, ...]:
    path = Path(source)
    if path.suffix != ".py":
        raise ValueError("Expected a Python source path")
    return tuple(path.parent.parts)


def _has_module(root: Path, name: str) -> bool:
    if not name:
        return False
    base = root.joinpath(*name.split("."))
    return base.with_suffix(".py").is_file() or base.is_dir()


def import_targets(tree: ast.AST, source: str, *, root: Path | None = None) -> list[str]:
    """Return static import targets including resolvable package submodules.

    These edges may be conditional or deferred. Computed dynamic imports are
    intentionally not guessed; invalid upward imports are omitted.
    """
    package = _package_parts(source)
    targets: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            targets.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                if node.level > len(package):
                    continue
                parts = package[:len(package) - node.level + 1]
                if node.module:
                    parts += tuple(node.module.split("."))
                base = ".".join(parts)
            else:
                base = node.module or ""
            if base:
                targets.add(base)
            if root is not None:
                for alias in node.names:
                    if alias.name == "*":
                        continue
                    candidate = ".".join(filter(None, (base, alias.name)))
                    if _has_module(Path(root), candidate):
                        targets.add(candidate)
    return sorted(targets)
