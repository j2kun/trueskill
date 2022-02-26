'''A bare-bones implementation of two-player TrueSkill.'''

from dataclasses import dataclass
from math import sqrt
from statistics import NormalDist
from typing import Tuple


DEFAULT_MEAN = 25
DEFAULT_STD_DEV = DEFAULT_MEAN / 3
DEFAULT_VARIANCE = DEFAULT_STD_DEV ** 2

SKILL_CLASS_WIDTH = (DEFAULT_STD_DEV / 2) ** 2
ADDITIVE_DYNAMICS_FACTOR = (DEFAULT_STD_DEV / 100) ** 2
DRAW_PROBABILITY = 0.01  # 1 percent
TOLERANCE = 1e-18

STANDARD_NORMAL = NormalDist(0, 1)


@dataclass(frozen=True)
class Rating:
    mean: float = DEFAULT_MEAN
    stddev: float = DEFAULT_STD_DEV


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


# TODO: add plots for these...
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


def truncated_twosided_gaussian_w(perf_diff, draw_margin):
    '''Equation 4.4 from Herbrich '05, On Gaussian Expectation Propagation.

    Representing the additive correction factor to the variance of a rectified
    Gaussian that is truncated on both sides.
    '''
    abs_diff = abs(perf_diff)
    normalization = (
        STANDARD_NORMAL.cdf(draw_margin - abs_diff) -
        STANDARD_NORMAL.cdf(-draw_margin - abs_diff)
    )
    if normalization < TOLERANCE:
        return 1

    v_value = truncated_twosided_gaussian_v(
        perf_diff, -draw_margin, draw_margin)
    t1 = (draw_margin - abs_diff) * STANDARD_NORMAL.pdf(draw_margin - abs_diff)
    t2 = (-draw_margin - abs_diff) * \
        STANDARD_NORMAL.pdf(-draw_margin - abs_diff)
    return v_value ** 2 + (t1 - t2) / normalization


def update_one_player(p1_rating, p2_rating, outcome):
    draw_margin = compute_draw_margin()
    c = sqrt(p1_rating.stddev**2 + p2_rating.stddev**2 + 2*SKILL_CLASS_WIDTH)
    winning_mean = p1_rating.mean if outcome >= 0 else p2_rating.mean
    losing_mean = p2_rating.mean if outcome >= 0 else p1_rating.mean
    perf_diff = winning_mean - losing_mean

    if outcome == 0:
        v = truncated_twosided_gaussian_v(
            perf_diff / c, -draw_margin / c, draw_margin / c)
        w = truncated_twosided_gaussian_w(perf_diff / c, draw_margin / c)
        mean_adjustment_direction = 1
    else:
        v = truncated_onesided_gaussian_v(perf_diff / c, draw_margin / c)
        w = truncated_onesided_gaussian_w(perf_diff / c, draw_margin / c)
        mean_adjustment_direction = outcome

    mean_multiplier = (p1_rating.mean ** 2 + ADDITIVE_DYNAMICS_FACTOR) / c
    variance_plus_dynamics = p1_rating.stddev ** 2 + ADDITIVE_DYNAMICS_FACTOR
    stddev_multiplier = variance_plus_dynamics / (c ** 2)

    new_mean = p1_rating.mean + mean_adjustment_direction * mean_multiplier * v
    new_stddev = sqrt(variance_plus_dynamics*(1 - w * stddev_multiplier))

    return Rating(mean=new_mean, stddev=new_stddev)


def update_ratings(
        p1_rating: Rating,
        p2_rating: Rating,
        outcome: int = 1) -> Tuple[Rating, Rating]:
    return (
        update_one_player(p1_rating, p2_rating, outcome),
        update_one_player(p2_rating, p1_rating, -outcome),
    )
