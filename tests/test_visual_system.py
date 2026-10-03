"""Generic color-domain and exact-table regressions for the notebook renderer."""
import unittest
from test_runtime import all_kinds_spec, page_result

class HeatmapScaleTests(unittest.TestCase):
    def inspect(self, values, invariant=False, actions=''):
        spec = all_kinds_spec()
        spec['controls'][-1]['default'] = values
        if invariant:
            spec['invariants'].append(dict(name='Declared unit interval', output='scaled_field', kind='range', min=0, max=1, atol=0, rtol=0))
        return page_result(spec, actions, "{scales:nodes.filter(n=>n.className==='scale-caption').map(n=>n.textContent),fills:nodes.filter(n=>n.tag==='rect').map(n=>n.attrs.fill),cells:nodes.filter(n=>n.tag==='td').map(n=>n.textContent)}")

    def test_declared_unit_interval_survives_edits(self):
        first=self.inspect([[0.2,0.3],[0.4,0.5]], True)
        second=self.inspect([[0.2,0.3],[0.4,0.5]], True, "change('input-field-1-1','0.9');")
        self.assertEqual(first['scales'], ['Fixed scale: 0 to 1 V'])
        self.assertEqual(first['scales'][-1], second['scales'][-1])
        self.assertEqual(first['fills'][-4:-1], second['fills'][-4:-1])

    def test_signed_data_uses_symmetric_scale_and_neutral_zero(self):
        result=self.inspect([[-2,0],[1,4]])
        self.assertEqual(result['scales'], ['Current scale: -4 to 4 V'])
        self.assertEqual(result['fills'][-3], 'rgb(245,246,246)')
        self.assertNotEqual(result['fills'][-4], result['fills'][-1])

    def test_one_sided_and_constant_data_stay_sequential(self):
        for values, scale in [([[2,3],[4,5]],'2 to 5'),([[-5,-4],[-3,-2]],'-5 to -2'),([[0,0],[0,0]],'0 to 1'),([[-2,-2],[-2,-2]],'-2 to 0')]:
            with self.subTest(values=values):
                self.assertEqual(self.inspect(values)['scales'], ['Current scale: '+scale+' V'])

    def test_numeric_tables_keep_full_precision(self):
        result=self.inspect([[0.123456789012345,0],[0,1]])
        self.assertIn('0.123456789012345', result['cells'])
