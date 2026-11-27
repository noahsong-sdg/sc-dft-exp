import copy
import unittest

from anisotropic_moment_analysis import cell_orbits, coefficients, contract, check_constant_controls

IDENTITY = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
SWAP = ((0, 1, 0), (1, 0, 0), (0, 0, 1))


class AnisotropicMomentTests(unittest.TestCase):
    def fixture(self, constant=False):
        orbits = [cell_orbits(2, [IDENTITY, SWAP], side) for side in (0, 1)]
        raw = dict(xi0=[.2], dx0=[.5], dos=[1.]*16,
                   first=[.01*(i-3) for i in range(16)],
                   second=[(-1 if i % 3 == 0 else 1)*.003*(i+1) for i in range(16)],
                   curvature=[.002*(i-5) for i in range(16)])
        avg = copy.deepcopy(raw)
        for side in (0, 1):
            for orbit in orbits[side]:
                indices = [cell-1+8*side for cell in orbit]
                for name in ('dos', 'first', 'second', 'curvature'):
                    value = sum(raw[name][i] for i in indices)/len(indices)
                    for i in indices:
                        avg[name][i] = value
        thermal = {i: coefficients(.2, .1 if constant else .03*(i+1), 10.) for i in range(16)}
        return raw, avg, thermal, orbits

    def evaluate(self, raw, avg, thermal, orbits):
        return contract([1, 1, 1, 8, 2], [.1, 10., .1, 0., 0.], raw, avg, thermal, orbits)

    def test_signed_weights_noninvariant_candidate_obeys_bound(self):
        raw, avg, thermal, orbits = self.fixture()
        result = self.evaluate(raw, avg, thermal, orbits)
        self.assertTrue(any(abs(r['averaging_difference']) > 1e-6 for r in result['grids']))
        for row in result['grids']:
            self.assertLessEqual(abs(row['averaging_difference']), row['averaging_absolute_bound']+1e-14)
            self.assertGreater(row['raw_cancellation_ratio'], 1.)

    def test_constant_gap_zero_range_and_averaging_effect(self):
        for row in self.evaluate(*self.fixture(constant=True))['grids']:
            self.assertAlmostEqual(row['averaging_difference'], 0., places=14)
            self.assertEqual(row['coefficient_range_bound'], 0.)
            self.assertLessEqual(abs(row['averaging_difference']), row['averaging_absolute_bound'])

    def test_native_constant_control_binding_and_stale_context(self):
        _, avg, _, _ = self.fixture()
        controls = dict(dimensions=[1, 1, 1, 16, 8], qnorm=.1, volume=10., cases=[])
        for temperature in (2, 4, 8):
            t, h = coefficients(.2, 1.5/13605.693122994, 157887.51240203338/temperature)
            row = dict(temperature_kelvin=temperature)
            for name in ('mean_squared_active', 'second_moment_active', 'second_moment_all'):
                row[name] = []
                for side in (0, 1):
                    values = range(8*side, 8*(side+1))
                    moment = lambda i: (avg['first'][i]**2/avg['dos'][i]
                        if name == 'mean_squared_active' else avg['second'][i])
                    row[name].append(sum(5*(t*moment(i)+h*avg['curvature'][i]) for i in values))
            controls['cases'].append(row)
        dims, physical = [1, 1, 1, 8, 2], [.1, 10., .1, 0., 0.]
        self.assertLess(check_constant_controls(dims, physical, avg, controls), 1e-12)
        stale = copy.deepcopy(controls)
        stale['cases'][0]['second_moment_all'][0] += .1
        with self.assertRaisesRegex(ValueError, 'constant-gap control'):
            check_constant_controls(dims, physical, avg, stale)
        stale = {**controls, 'qnorm': .2}
        with self.assertRaisesRegex(ValueError, 'context'):
            check_constant_controls(dims, physical, avg, stale)

    def test_bad_native_replay_or_nonclosed_support_rejected(self):
        raw, avg, thermal, orbits = self.fixture()
        avg['second'][2] += .01
        with self.assertRaisesRegex(ValueError, 'replay'):
            self.evaluate(raw, avg, thermal, orbits)
        raw, avg, thermal, orbits = self.fixture()
        del thermal[2]
        with self.assertRaisesRegex(ValueError, 'support'):
            self.evaluate(raw, avg, thermal, orbits)
        with self.assertRaisesRegex(ValueError, 'Nonuniform'):
            cell_orbits(2, [IDENTITY, IDENTITY, SWAP], 0)


if __name__ == '__main__':
    unittest.main()
