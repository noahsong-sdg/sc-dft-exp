"""Add one occupation-defect direction using an already measured full image.

Columns Q are orthonormal, U=A0 Q, and image=A0 f. This identity does not
establish consistency of externally supplied operator actions or gap accuracy.
"""
import math
import sys


def dot(a, b):
    return math.fsum(x*y for x, y in zip(a, b))


def combine(columns, coefficients):
    return [dot(row, coefficients) for row in zip(*columns)]


def enrich(q, u, occupation, image):
    n, rank = len(occupation), len(q)
    if not 1 <= rank < n or len(u) != rank or len(image) != n or any(len(c) != n for c in (*q, *u)):
        raise ValueError('Incompatible enrichment dimensions')
    if not all(math.isfinite(x) for c in (*q, *u, occupation, image) for x in c):
        raise ValueError('Nonfinite enrichment input')
    orth = max(abs(dot(a, b)-(i == j)) for i, a in enumerate(q) for j, b in enumerate(q))
    if orth > 1e-10:
        raise ValueError('Enrichment requires an orthonormal basis')
    coefficients = [dot(c, occupation) for c in q]
    defect = [a-b for a, b in zip(occupation, combine(q, coefficients))]
    action = [a-b for a, b in zip(image, combine(u, coefficients))]
    # Apply exactly the same subtractions to the direction and its linear image.
    for _ in range(2):
        correction = [dot(c, defect) for c in q]
        defect = [a-b for a, b in zip(defect, combine(q, correction))]
        action = [a-b for a, b in zip(action, combine(u, correction))]
    norm = math.sqrt(dot(defect, defect))
    scale = math.sqrt(dot(occupation, occupation))
    if norm <= 128*sys.float_info.epsilon*scale or norm == 0:
        raise ValueError('Occupation defect is numerically unresolved')
    direction = [x/norm for x in defect]
    new_image = [x/norm for x in action]
    if not all(map(math.isfinite, (*direction, *new_image))):
        raise ValueError('Nonfinite normalized enrichment')
    return direction, new_image, dict(
        occupation_defect_norm=norm, relative_occupation_defect_norm=norm/scale,
        new_direction_old_basis_overlap=max(abs(dot(c, direction)) for c in q),
        new_direction_norm=math.sqrt(dot(direction, direction)),
        inherited_operator_consistency_verified=False)
