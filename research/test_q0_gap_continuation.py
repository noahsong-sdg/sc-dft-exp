"""Independent finite-Q occupation control of the fixed-gap slope limit."""
from decimal import Decimal, localcontext
import unittest

from linear_response import stiffness


STATES = ((.3,.2,.7,.6,.2),(-.7,.4,-.15,-.3,-.07),(0.,.1,.8,.4,.1))


def current_over_q(q,beta,continuation):
    with localcontext() as context:
        context.prec=60
        d=lambda value:Decimal(str(value))
        terms=[]
        for xi,gap,weight,a,b in STATES:
            gap=d(continuation(gap,q))
            xi,weight,a,b=map(d,(xi,weight,a,b))
            momentum=d(q);inverse_temperature=d(beta)
            xi=xi+b*momentum*momentum
            energy=(xi*xi+gap*gap).sqrt()
            shift=abs(a*momentum)
            def occupations(y):
                plus=(inverse_temperature*(y+shift)).exp()
                minus=(inverse_temperature*(y-shift)).exp()
                plus=(plus-1)/(plus+1);minus=(minus-1)/(minus+1)
                return (plus+minus)/2,(plus-minus)/2
            normal,normal_difference=occupations(abs(xi))
            paired,paired_difference=occupations(energy)
            signed_normal=normal if xi>=0 else -normal
            numerator=(2*shift*(normal_difference-paired_difference)
                +4*b*momentum*momentum*(signed_normal-xi/energy*paired))
            terms.append(weight*(1+d(.2)*momentum*momentum)*numerator/(momentum*momentum))
        return float(sum(terms))


class Q0GapContinuationTests(unittest.TestCase):
    def test_fixed_and_varying_gap_paths_share_the_analytic_limit(self):
        for beta in (2.,8.,40.):
            expected=stiffness(STATES,beta)
            for slope in (0.,.3,-.2):
                with self.subTest(beta=beta,slope=slope):
                    continuation=lambda gap,q:gap+slope*q+.7*q*q
                    errors=[abs(current_over_q(q,beta,continuation)-expected)
                            for q in (1e-3,1e-4,1e-5,1e-6)]
                    self.assertLess(errors[1],errors[0]/5)
                    self.assertLess(errors[2],errors[1]/5)
                    self.assertLess(errors[3],errors[2]/5)
                    self.assertLess(errors[3],2e-5)

    def test_even_gap_path_preserves_signed_momentum_limit(self):
        continuation=lambda gap,q:gap+.7*q*q
        for q in (1e-3,1e-4):
            self.assertEqual(current_over_q(q,8.,continuation),
                             current_over_q(-q,8.,continuation))

    def test_discontinuous_gap_path_does_not_qualify_the_original_gap(self):
        changed=lambda gap,q:gap+.08
        expected=stiffness(STATES,8.)
        alternate=stiffness([(x,g+.08,w,a,b) for x,g,w,a,b in STATES],8.)
        measured=current_over_q(1e-5,8.,changed)
        self.assertAlmostEqual(measured,alternate,delta=1e-8)
        self.assertGreater(abs(measured-expected),1e-3)


if __name__=='__main__':unittest.main()
