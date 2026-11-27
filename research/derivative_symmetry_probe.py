"""Independent cubic BCC band control for primitive-direction derivatives.

This is an analytic stencil control, not niobium or a penetration-depth model.
The Gaussian energy weight is cubic invariant and chosen only for this control.
"""
import json
import math
from itertools import product


def band(k):
    first=-8*math.prod(math.cos(x/2) for x in k)
    third=-.4*sum(math.cos(k[a])*math.cos(k[b]) for a,b in ((0,1),(1,2),(2,0)))
    return first+third


def gradient(k):
    return [4*math.sin(k[a]/2)*math.prod(math.cos(k[b]/2) for b in range(3) if b!=a)
            +.4*math.sin(k[a])*sum(math.cos(k[b]) for b in range(3) if b!=a)
            for a in range(3)]


def evaluate(n):
    sums=[[0.,0.] for _ in range(3)]
    for indices in product(range(n),repeat=3):
        # Primitive reciprocal columns are 2*pi*(011), (101), (110).
        k=[2*math.pi*(sum(indices)-indices[a])/n for a in range(3)]
        weight=math.exp(-band(k)**2/2)
        primitive=[[],[]]
        for axis in range(3):
            shifted={m:band([x+(0 if a==axis else 2*math.pi*m/n)
                             for a,x in enumerate(k)]) for m in (-2,-1,1,2)}
            primitive[0].append(n*(shifted[1]-shifted[-1])/2)
            primitive[1].append(n*(-shifted[2]+8*shifted[1]-8*shifted[-1]+shifted[-2])/12)
        # Inverse-transpose reciprocal basis converts coordinate derivatives.
        vectors=[[(sum(g)-2*g[a])/(4*math.pi) for a in range(3)] for g in primitive]
        vectors.append(gradient(k))
        for total,v in zip(sums,vectors):
            total[0]+=weight*((v[1]+v[2])/math.sqrt(2))**2
            total[1]+=weight*(sum(v)/math.sqrt(3))**2
    errors=[b/a-1 for a,b in sums]
    return dict(grid=n,second_order_relative_direction_difference=errors[0],
                fourth_order_relative_direction_difference=errors[1],
                analytic_relative_direction_difference=errors[2])


def run():
    cases=[evaluate(n) for n in (8,16,32)]
    if any(abs(row['analytic_relative_direction_difference'])>1e-12 for row in cases):
        raise AssertionError('Analytic cubic reference is not isotropic')
    if any(abs(row['fourth_order_relative_direction_difference'])>=
           abs(row['second_order_relative_direction_difference']) for row in cases):
        raise AssertionError('Higher-order stencil failed this analytic control')
    return dict(cases=cases,scope='Analytic cubic band velocity-squared quadrature; not a material response')


if __name__=='__main__':print(json.dumps(run(),indent=2))
