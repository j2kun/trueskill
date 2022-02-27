'''Math functions for hard-coded formulas used in inference steps.
'''
from math import sqrt
from statistics import NormalDist

from constants import DRAW_PROBABILITY
from constants import SKILL_CLASS_WIDTH
from constants import TOLERANCE

STANDARD_NORMAL = NormalDist(0, 1)


def compute_draw_margin() -> float:
    '''
      The margin to use to consider the game a draw, based on the (pre-set)
      probability of a draw, which is typically set by measuring the draw rates
      of a large number of games. Derived by inverting the formula

        P(draw) = -1 + 2 * normal_cdf(
            draw_margin / sqrt(player_count * skill_class_width)
        )

      or, as written exactly in the paper,

        P(draw) = -1 + 2 * normal_cdf(
            draw_margin / (sqrt(n1 + n2) * beta)
        )
    '''
    inv_cdf_arg = 0.5 * (DRAW_PROBABILITY + 1)
    inv_cdf_output = STANDARD_NORMAL.inv_cdf(inv_cdf_arg)
    return inv_cdf_output * sqrt(2 * SKILL_CLASS_WIDTH)


def truncated_onesided_gaussian_v(t: float, lower: float) -> float:
    '''Equation 4.7 from Herbrich '05, On Gaussian Expectation Propagation.

    Representing the additive correction factor to the mean of a rectified
    Gaussian that is only truncated from below.

    This function grows roughly like lower - t for t < lower and quickly
    approaches zero for t > lower.
    '''
    normalization = STANDARD_NORMAL.cdf(t - lower)
    if normalization < TOLERANCE:
        return lower - t   # approaches infinity
    return STANDARD_NORMAL.pdf(t - lower) / normalization


def truncated_onesided_gaussian_w(t: float, lower: float) -> float:
    '''Equation 4.8 from Herbrich '05, On Gaussian Expectation Propagation.

    Representing the additive correction factor to the variance of a rectified
    Gaussian that is only truncated from below. This is a smooth approximation
    to an indicator function for the condition t <= lower.
    '''
    v_value = truncated_onesided_gaussian_v(t, lower)
    return v_value * (v_value + t - lower)


def truncated_twosided_gaussian_v(t, lower, upper):
    '''Equation 4.4 from Herbrich '05, On Gaussian Expectation Propagation.

    Representing the additive correction factor to the mean of a rectified
    Gaussian that is truncated on both sides.
    '''
    normalization = (STANDARD_NORMAL.cdf(upper - t) -
                     STANDARD_NORMAL.cdf(lower - t))
    if normalization < TOLERANCE:
        # the limit as upper -> lower
        return lower - t

    return (
        STANDARD_NORMAL.pdf(lower - t) - STANDARD_NORMAL.pdf(upper - t)
    ) / normalization


def truncated_twosided_gaussian_w(t, lower, upper):
    '''Equation 4.4 from Herbrich '05, On Gaussian Expectation Propagation.

    Representing the additive correction factor to the variance of a rectified
    Gaussian that is truncated on both sides.
    '''
    normalization = (
        STANDARD_NORMAL.cdf(upper - t) - STANDARD_NORMAL.cdf(lower - t)
    )
    if normalization < TOLERANCE:
        return 1

    v = truncated_twosided_gaussian_v(t, lower, upper)
    t1 = (upper - t) * STANDARD_NORMAL.pdf(upper - t)
    t2 = (lower - t) * STANDARD_NORMAL.pdf(lower - t)
    return v**2 + (t1 - t2) / normalization
