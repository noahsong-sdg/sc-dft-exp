"""Normalize saved four-image batches, including actual perturbed residuals."""
import array
import math


def corrected_states(images, gap, direction, z, counts, step):
    if len(counts) != 3 or min(counts) <= 0 or counts[2] != max(counts[:2]):
        raise ValueError('Invalid correction image dimensions')
    n = 2*counts[2]
    if len(images) != 4*n or any(len(x) != n for x in (gap,direction,z)):
        raise ValueError('Stale correction image shape')
    if (not math.isfinite(step) or step <= 0 or not math.isfinite(2*step)
            or not all(math.isfinite(x) for block in (images,gap,direction,z) for x in block)
            or max(map(abs,direction)) != 1 or any(1+x <= 0 for x in z)):
        raise ValueError('Invalid correction state/step')
    plus = array.array('d', (d+step*v for d,v in zip(gap,direction)))
    minus = array.array('d', (d-step*v for d,v in zip(gap,direction)))
    residuals = [array.array('d', [0.])*n for _ in range(3)]
    jacobian = array.array('d', [0.])*n
    for side,active in enumerate(counts[:2]):
        begin = side*counts[2]
        for i in range(begin+active,begin+counts[2]):
            if gap[i] != 0 or direction[i] != 0 or any(images[k*n+i] != 0 for k in range(4)):
                raise ValueError('Nonzero correction padding')
        for i in range(begin,begin+active):
            for k,point in enumerate((gap,plus,minus)):
                residuals[k][i] = -images[k*n+i]/(1+z[i])-point[i]
            jacobian[i] = -images[3*n+i]/(1+z[i])-direction[i]
    blocks = (plus,minus,*residuals,jacobian)
    if not all(math.isfinite(x) for block in blocks for x in block):
        raise ValueError('Nonfinite corrected image normalization')
    fd_error = max(abs((a-b)/(2*step)-j) for a,b,j in zip(residuals[1],residuals[2],jacobian))
    fd_bound = 1e-8+2e-6*max(map(abs,jacobian))
    if not math.isfinite(fd_error) or fd_error > fd_bound:
        raise ValueError('Corrected image finite difference mismatch')
    summaries = []
    for point,residual in zip((gap,plus,minus),residuals):
        norm2 = math.fsum(x*x for x in point)
        if norm2 == 0 or not math.isfinite(norm2):
            raise ValueError('Invalid corrected gap norm')
        rinf = max(map(abs,residual)); relative = math.sqrt(math.fsum(x*x for x in residual)/norm2)
        if not math.isfinite(relative):
            raise ValueError('Nonfinite corrected residual summary')
        summaries.append(dict(residual_infinity_ry=rinf, residual_over_gap_rms=relative,
                              stationary_residual_targets_met=rinf<=1e-10 and relative<=1e-5))
    return dict(plus_gap=plus,minus_gap=minus,residuals=residuals,jacobian=jacobian,
                summaries=summaries,independent_fd_error=fd_error,independent_fd_bound=fd_bound,
                conditioned_gap_error_bounded=False,physical_response_verified=False)
