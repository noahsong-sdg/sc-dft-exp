"""Independent continuum density control of the fixed-gap current slope.

Dispersion xi_Ry=k^2-mu, two spin states, unit-cell volume1.
Finite radial cutoff is shared by both integrals; this is not a material test.
"""
import math
import unittest

from linear_response import sech2, stiffness


def radial_control(beta, gap, intervals=8192, cutoff=4.):
    step=cutoff/intervals
    states=[];density=[];normal=[]
    for i in range(intervals+1):
        k=i*step;xi=k*k-.93;energy=math.hypot(xi,gap)
        simpson=1 if i in (0,intervals) else 4 if i%2 else 2
        weight=step*simpson/3*k*k/(2*math.pi**2)
        # Half-shift Q/2: directional <a^2>=k^2/3, b=1/4.
        states.append((xi,gap,weight,k/math.sqrt(3),.25))
        density.append(weight*(1-xi/energy*math.tanh(beta*energy/2)))
        normal.append(weight*beta*k*k/3*sech2(beta*energy/2))
    xi_edge=cutoff*cutoff-.93
    # Integration by parts of the NORMAL reference at the same finite cutoff.
    tail=math.exp(-beta*xi_edge)
    boundary=cutoff**3/(6*math.pi**2)*2*tail/(1+tail)
    return states,math.fsum(density),math.fsum(normal),boundary


class ParabolicCurrentNormalizationTest(unittest.TestCase):
    def test_slope_equals_paired_density_minus_normal_fluid(self):
        for beta in (4.,12.,40.,120.):
            for gap in (0.,.15,.4):
                with self.subTest(beta=beta,gap=gap):
                    states,density,normal,boundary=radial_control(beta,gap)
                    expected=density-normal-boundary
                    self.assertAlmostEqual(stiffness(states,beta),expected,delta=2e-11)

    def test_rydberg_to_hartree_scales_slope_by_one_half(self):
        beta=12.
        states,_,_,_=radial_control(beta,.15)
        hartree=[(xi/2,gap/2,w,a/2,b/2) for xi,gap,w,a,b in states]
        self.assertAlmostEqual(2*stiffness(hartree,2*beta),stiffness(states,beta),delta=1e-15)

    def test_normal_state_and_low_temperature_density_limits(self):
        states,_,_,_=radial_control(12.,0.)
        self.assertEqual(stiffness(states,12.),0.)
        states,density,normal,_=radial_control(120.,.4)
        self.assertLess(normal/density,1e-16)
        self.assertAlmostEqual(stiffness(states,120.)/density,1.,delta=1e-9)


if __name__=='__main__':unittest.main()
