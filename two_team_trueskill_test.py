'''Tests for two_team_trueskill.py'''

from trueskill_types import Rating
from trueskill_types import Team
from trueskill_types import Player
from two_team_trueskill import update_ratings

p1 = Player(1)
p2 = Player(2)
p3 = Player(3)
p4 = Player(4)


def test_unsurprising_t1_win():
    p1_rating = Rating(mean=10, stddev=1)
    p2_rating = Rating(mean=11, stddev=1)
    p3_rating = Rating(mean=2, stddev=1)
    p4_rating = Rating(mean=3, stddev=1)

    team1 = Team(ratings={
        p1: p1_rating,
        p2: p2_rating,
    })
    team2 = Team(ratings={
        p3: p3_rating,
        p4: p4_rating,
    })

    outcome = 1
    new_ratings = update_ratings(team1, team2, outcome)

    new_p1_rating = new_ratings[p1]
    new_p2_rating = new_ratings[p2]
    new_p3_rating = new_ratings[p3]
    new_p4_rating = new_ratings[p4]

    assert new_p1_rating.mean > p1_rating.mean
    assert new_p2_rating.mean > p2_rating.mean
    assert new_p3_rating.mean < p3_rating.mean
    assert new_p4_rating.mean < p4_rating.mean


def test_surprising_t2_win():
    p1_rating = Rating(mean=10, stddev=0.1)
    p2_rating = Rating(mean=11, stddev=0.1)
    p3_rating = Rating(mean=2, stddev=0.1)
    p4_rating = Rating(mean=3, stddev=0.1)

    team1 = Team(ratings={
        p1: p1_rating,
        p2: p2_rating,
    })
    team2 = Team(ratings={
        p3: p3_rating,
        p4: p4_rating,
    })

    outcome = -1
    new_ratings = update_ratings(team1, team2, outcome)

    new_p1_rating = new_ratings[p1]
    new_p2_rating = new_ratings[p2]
    new_p3_rating = new_ratings[p3]
    new_p4_rating = new_ratings[p4]

    assert new_p1_rating.mean < p1_rating.mean
    assert new_p2_rating.mean < p2_rating.mean
    assert new_p3_rating.mean > p3_rating.mean
    assert new_p4_rating.mean > p4_rating.mean
    assert new_p1_rating.stddev > p1_rating.stddev
    assert new_p2_rating.stddev > p2_rating.stddev
    assert new_p3_rating.stddev > p3_rating.stddev
    assert new_p4_rating.stddev > p4_rating.stddev
    assert (
        new_p1_rating.mean + new_p2_rating.mean
        < p3_rating.mean + p4_rating.mean
    )
