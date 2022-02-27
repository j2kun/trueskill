'''A bare-bones implementation of two-team TrueSkill.'''

from math import sqrt
from typing import Dict

from constants import ADDITIVE_DYNAMICS_FACTOR
from constants import SKILL_CLASS_WIDTH
from trueskill_math import compute_draw_margin
from trueskill_math import truncated_onesided_gaussian_v
from trueskill_math import truncated_onesided_gaussian_w
from trueskill_math import truncated_twosided_gaussian_v
from trueskill_math import truncated_twosided_gaussian_w
from trueskill_types import Player
from trueskill_types import Rating
from trueskill_types import Team


def update_one_team(
        team1: Team, team2: Team, outcome: int) -> Dict[Player, Rating]:
    '''Return the new ratings for team1.'''
    # The logic between here and the for loop over individual player updates
    # is identical to the two-player update, where each "player" is represented
    # by the team-wide sum of player skill means/variances, with an appropriate
    # scaling by player_count.
    draw_margin = compute_draw_margin()
    player_count = len(team1.ratings) + len(team2.ratings)
    t1_mean = sum(p.mean for p in team1.ratings.values())
    t2_mean = sum(p.mean for p in team2.ratings.values())
    t1_variance = sum(p.stddev ** 2 for p in team1.ratings.values())
    t2_variance = sum(p.stddev ** 2 for p in team2.ratings.values())

    c = sqrt(t1_variance + t2_variance + player_count*SKILL_CLASS_WIDTH)
    winning_mean = t1_mean if outcome >= 0 else t2_mean
    losing_mean = t2_mean if outcome >= 0 else t1_mean
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

    # Here we propagate the rating adjustment data from the team-wide summed
    # skills down to each player. The updates are the same as the two-player
    # case for each player, except that the normalization constant c is scaled
    # up according to the sum of variances and player counts, which impacts
    # both the value of c and the size of the multiplier that attributes team
    # performance back to the individual player.
    new_ratings: Dict[Player, Rating] = dict()
    for player, rating in team1.ratings.items():
        mean, stddev = rating.mean, rating.stddev
        mean_multiplier = (mean ** 2 + ADDITIVE_DYNAMICS_FACTOR) / c
        variance_plus_dynamics = stddev ** 2 + ADDITIVE_DYNAMICS_FACTOR
        stddev_multiplier = variance_plus_dynamics / (c ** 2)
        new_mean = mean + mean_adjustment_direction * mean_multiplier * v
        new_stddev = sqrt(variance_plus_dynamics*(1 - w * stddev_multiplier))
        new_ratings[player] = Rating(mean=new_mean, stddev=new_stddev)

    return new_ratings


def update_ratings(
        team1: Team,
        team2: Team,
        outcome: int = 1) -> Dict[Player, Rating]:
    # Nb: in Python3.9 the bitwise-or operator is overloaded for dictionaries
    # to perform a union of the key-value pairs. See PEP584.
    return (
        update_one_team(team1, team2, outcome) |
        update_one_team(team2, team1, -outcome)
    )
