'''A bare-bones implementation of two-player TrueSkill.'''

from math import sqrt
from typing import Tuple

from constants import ADDITIVE_DYNAMICS_FACTOR
from constants import SKILL_CLASS_WIDTH
from trueskill_math import compute_draw_margin
from trueskill_math import truncated_onesided_gaussian_v
from trueskill_math import truncated_onesided_gaussian_w
from trueskill_math import truncated_twosided_gaussian_v
from trueskill_math import truncated_twosided_gaussian_w
from trueskill_types import Rating


def update_one_player(
        p1_rating: Rating, p2_rating: Rating, outcome: int) -> Rating:
    draw_margin = compute_draw_margin()
    player_count = 2
    c = sqrt(
        p1_rating.stddev**2
        + p2_rating.stddev**2
        + player_count*SKILL_CLASS_WIDTH
    )
    winning_mean = p1_rating.mean if outcome >= 0 else p2_rating.mean
    losing_mean = p2_rating.mean if outcome >= 0 else p1_rating.mean
    perf_diff = winning_mean - losing_mean

    if outcome == 0:
        v = truncated_twosided_gaussian_v(
            perf_diff / c, -draw_margin / c, draw_margin / c)
        w = truncated_twosided_gaussian_w(
            perf_diff / c, -draw_margin / c, draw_margin / c)
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
