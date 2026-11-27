"""Independent high-precision oracle and held-out scalar thermal checks."""
import json
import math
from decimal import Decimal, localcontext
from current_identity import corrected_normal


def oracle(x,d,beta):
    with localcontext() as context:
        context.prec = 80
        x,d,beta = (Decimal(str(value)) for value in (x,d,beta))
        def thermal(z):
            # Saturation below 80-digit resolution, avoiding huge exponentials.
            if abs(z) > 200:
                return Decimal(1) if z > 0 else Decimal(-1)
            e = (2*z).exp()
            return (e-1)/(e+1)
        return float((thermal(beta*(x+d)/2)+thermal(beta*(x-d)/2))/2)


def stable_normal(x,d,beta):
    a = math.tanh(.5*beta*d)
    b = math.tanh(.5*beta*x)
    if 1-a*b < 1e-10:
        return .5*(math.tanh(.5*beta*(x+d))+math.tanh(.5*beta*(x-d)))
    return corrected_normal(x,d,beta)


def run():
    cases = [(x,d,beta) for beta in (.01,1.,10.,100.,1e4,1e6)
             for d in (1e-6,.1,1.,10.)
             for x in (d*(1-1e-8),d,d*(1+1e-8),d*.1,d*10)]
    rows = [dict(x=x,d=d,beta=beta,reference=oracle(x,d,beta),
                 absolute_error=abs(stable_normal(x,d,beta)-oracle(x,d,beta)))
            for x,d,beta in cases]
    worst = max(rows,key=lambda row:row["absolute_error"])
    return dict(cases=len(rows),decimal_precision=80,worst=worst,
                failures_above_1e_7=sum(row["absolute_error"]>1e-7 for row in rows),
                scope="Normal scalar thermal factor; no full current/material error bound")


if __name__ == "__main__":
    print(json.dumps(run(),indent=2,allow_nan=False))
