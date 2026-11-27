"""Validate saved current state records without guessing missing curvature."""
import math


def parse_current_record(line):
    fields = line.split()
    if len(fields) == 7:
        raise ValueError("Legacy five-float state lacks d2xq; current replay requires curvature")
    if len(fields) != 8:
        raise ValueError("Expected six floats and two integer indices")
    values = tuple(float(value.replace("D", "E")) for value in fields[:6])
    if not all(math.isfinite(value) for value in values):
        raise ValueError("Nonfinite saved state")
    indices = tuple(int(value) for value in fields[6:])
    if min(indices) < 1:
        raise ValueError("State indices must be positive")
    return values, indices
