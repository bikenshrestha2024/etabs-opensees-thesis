"""Fail if a public function/class in components/ lacks a [REF ...] docstring tag.

[REF docs/REF_TAG_CONVENTION.md] Ratchet: functions untagged on 2026-11-07
are listed in tests/data/ref_tag_baseline.json; the list may only shrink.

    python tests/verify_ref_tags.py                   # run the check
    python tests/verify_ref_tags.py --write-baseline  # remove entries now tagged/removed
"""
import ast
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / 'tests' / 'data' / 'ref_tag_baseline.json'
STRICT_EXTRA = ('tools/plot_results.py', 'tools/export_dashboard.py')
TAG = re.compile(r'\[REF [^\]]+\]')


def scanned_files():
    files = sorted((ROOT / 'components').rglob('*.py'))
    return files + [ROOT / p for p in STRICT_EXTRA if (ROOT / p).exists()]


def public_symbols():
    """Return {'path::name': has_tag} for top-level public functions and classes."""
    out = {}
    for path in scanned_files():
        rel = path.relative_to(ROOT).as_posix()
        tree = ast.parse(path.read_text(encoding='utf-8-sig'), filename=rel)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) \
                    and not node.name.startswith('_'):
                out[rel + '::' + node.name] = bool(TAG.search(ast.get_docstring(node) or ''))
    return out


def load_baseline():
    return set(json.loads(BASELINE.read_text(encoding='utf-8'))['untagged'])


class RefTags(unittest.TestCase):
    def test_new_public_symbols_are_tagged(self):
        missing = sorted(k for k, tagged in public_symbols().items()
                         if not tagged and k not in load_baseline())
        self.assertEqual(missing, [], 'Add a [REF ...] tag (docs/REF_TAG_CONVENTION.md) to: '
                         + ', '.join(missing))

    def test_baseline_only_shrinks(self):
        symbols = public_symbols()
        stale = sorted(k for k in load_baseline() if symbols.get(k, True))
        self.assertEqual(stale, [], 'Remove now-tagged/removed entries with '
                         '`python tests/verify_ref_tags.py --write-baseline`: ' + ', '.join(stale))

    def test_strict_files_have_no_baseline_entries(self):
        strict = [k for k in load_baseline() if k.split('::')[0] in STRICT_EXTRA]
        self.assertEqual(strict, [])

    def test_tag_syntax_detected(self):
        self.assertTrue(TAG.search('x [REF NBC105-2025 §5.5.3] y'))
        self.assertFalse(TAG.search('[REF]'))
        self.assertFalse(TAG.search('[REFERENCE NBC]'))


def write_baseline():
    symbols = public_symbols()
    old = load_baseline() if BASELINE.exists() else None
    untagged = {k for k, tagged in symbols.items() if not tagged}
    if old is not None:
        added = sorted(untagged - old)
        if added:
            raise SystemExit('Refusing to add untagged symbols to the baseline; tag them instead: '
                             + ', '.join(added))
        untagged &= old
    BASELINE.parent.mkdir(parents=True, exist_ok=True)
    BASELINE.write_text(json.dumps(dict(
        convention='docs/REF_TAG_CONVENTION.md',
        introduced='2026-11-07',
        note='Untagged public symbols at introduction. This list may only shrink.',
        untagged=sorted(untagged)), indent=1) + '\n', encoding='utf-8')
    print(f'{len(untagged)} baseline entries written to {BASELINE.relative_to(ROOT)}')


if __name__ == '__main__':
    if '--write-baseline' in sys.argv:
        write_baseline()
    else:
        unittest.main()
