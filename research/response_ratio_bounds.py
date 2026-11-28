"""Outward ratio enclosure for independently justified stiffness intervals."""
from fractions import Fraction
import math


def _outward(value, upward):
    try:
        result = float(value)
    except OverflowError as error:
        raise ValueError('Ratio enclosure exceeds finite binary64 range') from error
    if not math.isfinite(result):
        raise ValueError('Ratio enclosure exceeds finite binary64 range')
    rounded = Fraction.from_float(result)
    if (upward and rounded < value) or (not upward and rounded > value):
        result = math.nextafter(result, math.inf if upward else -math.inf)
    if not math.isfinite(result):
        raise ValueError('Ratio enclosure exceeds finite binary64 range')
    return result


def stiffness_ratio_interval(numerator, numerator_error, denominator, denominator_error):
    """Enclose N/D from absolute error bounds around finite binary64 centers.

    Bounds must already cover all intended errors. This routine assumes no
    cancellation or correlation, and supplies no missing physical uncertainty.
    Input floats are treated as exact values; output endpoints round outward.
    """
    values = (numerator, numerator_error, denominator, denominator_error)
    if not all(math.isfinite(x) for x in values) or min(numerator_error, denominator_error) < 0:
        raise ValueError('Finite centers and nonnegative absolute errors required')
    n, ne, d, de = map(Fraction.from_float, map(float, values))
    denominators = (d-de, d+de)
    if denominators[0] <= 0 <= denominators[1]:
        raise ValueError('Denominator interval must exclude zero')
    corners = [(n+s*ne)/endpoint for s in (-1, 1) for endpoint in denominators]
    return _outward(min(corners), False), _outward(max(corners), True)
