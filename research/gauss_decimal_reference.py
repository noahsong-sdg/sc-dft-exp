"""Independent 100-node quadrature diagnostic; not a production grid replacement.

Decimal Taylor cosine and a Legendre recurrence avoid the native libm seeds.
Check all polynomial moments through the Gauss rule's exact degree 199.
"""
from decimal import Decimal, localcontext
import json

PI = '3.141592653589793238462643383279502884197169399375105820974944592307816406286'


def reference():
    with localcontext() as context:
        context.prec = 75
        n = 100

        def cosine(x):
            term = total = Decimal(1)
            for k in range(1, 500):
                term *= -x*x/Decimal((2*k-1)*2*k)
                previous = total
                total += term
                if total == previous:
                    return total
            raise ArithmeticError('Taylor seed did not converge')

        def polynomials(x):
            previous, current = Decimal(1), x
            for j in range(1, n):
                previous, current = current, ((2*j+1)*x*current-j*previous)/(j+1)
            return current, previous

        nodes, weights = [], []
        for i in range(1, n+1):
            x = cosine(Decimal(PI)*(Decimal(n-i+1)-Decimal('.25'))/Decimal('100.5'))
            for iteration in range(100):
                p, previous = polynomials(x)
                derivative = n*(previous-x*p)/(1-x*x)
                step = p/derivative
                x -= step
                if abs(step) < Decimal('1e-65'):
                    break
            else:
                raise ArithmeticError('Legendre root did not converge')
            p, previous = polynomials(x)
            nodes.append(x)
            weights.append(2*(1-x*x)/(n*previous)**2)
        errors = [abs(sum((w*x**k for x, w in zip(nodes, weights)), Decimal(0))
            -(Decimal(2)/(k+1) if k % 2 == 0 else Decimal(0))) for k in range(200)]
        if max(errors) > Decimal('1e-60'):
            raise ArithmeticError('Polynomial exactness check failed')
        return dict(n=n, precision_decimal_digits=75, newton_step_stop='1e-65',
            max_absolute_moment_error_through_degree199=str(max(errors)),
            nodes_decimal=list(map(str, nodes)), weights_decimal=list(map(str, weights)),
            nodes_binary64=[float(x).hex() for x in nodes],
            weights_binary64=[float(w).hex() for w in weights],
            scope=__doc__, production_grid_replacement=False)


if __name__ == '__main__':
    print(json.dumps(reference(), indent=2))
