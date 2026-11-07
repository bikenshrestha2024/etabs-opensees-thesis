"""Section tag registry: defaults unchanged, overrides validated, ETABS names checked.

[REF components/model/section_tags.py; OpenSees section tag namespace]
Solver-free. Does not verify that a project nonlinear_materials_file actually
defines an overridden tag (needs a native build).
"""
import unittest
from pathlib import Path

from components.model.section_tags import (
    default_section_tags, resolve_nonlinear_section_tags, validate_frame_mapping)

ROOT = Path(__file__).resolve().parents[1]
FORMER_LITERAL = {'SHS_350x350x16_STEEL_FIBER': 701, 'RC_BEAM_600x800_FIBER': 611,
                  'RC_COLUMN_1100x1100_FIBER': 621, 'RC_COLUMN_1250x1250_FIBER': 631}


def frame(obj, section, **extra):
    return dict(object=obj, properties=dict(section=section), **extra)


class SectionTags(unittest.TestCase):
    def test_defaults_equal_former_hard_coded_literal(self):
        self.assertEqual(default_section_tags(), FORMER_LITERAL)
        self.assertEqual(resolve_nonlinear_section_tags({}), FORMER_LITERAL)
        self.assertEqual(resolve_nonlinear_section_tags({}, research=True), FORMER_LITERAL)

    def test_literal_removed_from_assembly_and_application(self):
        for name in ('components/model/assembly.py', 'components/ui/application.py'):
            src = (ROOT / name).read_text(encoding='utf-8')
            self.assertNotIn("'RC_COLUMN_1250x1250_FIBER':631", src, name)

    def test_reviewed_route_override_and_validation(self):
        tags = resolve_nonlinear_section_tags(
            {'nonlinear_section_tags': {'RC_COLUMN_900x900_FIBER': 641}})
        self.assertEqual(tags['RC_COLUMN_900x900_FIBER'], 641)
        for bad in ({'X': True}, {'X': 0}, {'X': 500000}, {'X': 611}, {'': 5}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                resolve_nonlinear_section_tags({'nonlinear_section_tags': bad})

    def test_research_route_rejects_tags_it_does_not_define(self):
        with self.assertRaises(ValueError):
            resolve_nonlinear_section_tags(
                {'nonlinear_section_tags': {'RC_BEAM_600x800_FIBER': 612}}, research=True)
        with self.assertRaises(ValueError):
            resolve_nonlinear_section_tags(
                {'nonlinear_section_tags': {'NEW': 640}}, research=True)

    def test_etabs_section_names_checked_before_build(self):
        tags = default_section_tags()
        data = dict(frames=[frame('B1', 'Beam 600*800'), frame('C1', 'Col 1100*1100'),
                            frame('BR1', 'SHS', hinged_brace=True), frame('D1', 'SHS')])
        cfg = dict(frame_section_mapping={'Beam 600*800': 'RC_BEAM_600x800_FIBER',
                                          'Col 1100*1100': 'RC_COLUMN_1100x1100_FIBER',
                                          'Old section': 'RC_BEAM_600x800_FIBER'})
        overrides = {'FRAME:D1': dict(target='FVD_MAXWELL')}
        out = validate_frame_mapping(data, cfg, tags, overrides=overrides, research=True)
        self.assertEqual(out['unused_mapping_keys'], ['Old section'])
        cfg['frame_section_mapping'].pop('Col 1100*1100')
        with self.assertRaisesRegex(ValueError, 'Col 1100\\*1100'):
            validate_frame_mapping(data, cfg, tags, overrides=overrides, research=True)
        cfg['frame_section_mapping']['Col 1100*1100'] = 'RC_COLUMN_900x900_FIBER'
        with self.assertRaisesRegex(ValueError, 'registered nonlinear section tag'):
            validate_frame_mapping(data, cfg, tags, overrides=overrides, research=True)


if __name__ == '__main__':
    unittest.main()
