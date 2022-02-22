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


def truncated_gaussian_v(perf_diff, draw_margin):
    normalization = STANDARD_NORMAL.cdf(perf_diff - draw_margin)
    if normalization < TOLERANCE:
        return -perf_diff + draw_margin
    return STANDARD_NORMAL.pdf(perf_diff - draw_margin) / normalization


def truncated_gaussian_w(perf_diff, draw_margin):
    normalization = STANDARD_NORMAL.cdf(perf_diff - draw_margin)
    if normalization < TOLERANCE:
        return int(perf_diff < 0)
    v_value = truncated_gaussian_v(perf_diff, draw_margin)
    return v_value * (v_value + perf_diff - draw_margin)


def update_one_player(p1_rating, p2_rating, outcome):
    draw_margin = compute_draw_margin()
    c = sqrt(p1_rating.stddev**2 + p2_rating.stddev**2 + 2*SKILL_CLASS_WIDTH)
    winning_mean = p1_rating.mean if outcome >= 0 else p2_rating.mean
    losing_mean = p2_rating.mean if outcome >= 0 else p1_rating.mean
    perf_diff = winning_mean - losing_mean

    # TODO: add draw case
    v = truncated_gaussian_v(perf_diff / c, draw_margin / c)
    w = truncated_gaussian_w(perf_diff / c, draw_margin / c)

    mean_multiplier = (p1_rating.mean ** 2 + ADDITIVE_DYNAMICS_FACTOR) / c
    variance_plus_dynamics = p1_rating.stddev ** 2 + ADDITIVE_DYNAMICS_FACTOR
    stddev_multiplier = variance_plus_dynamics / (c ** 2)

    new_mean = p1_rating.mean + outcome * mean_multiplier * v
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
