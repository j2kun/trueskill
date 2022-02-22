'''Tests for two_player_trueskill.py'''

from two_player_trueskill import Rating
from two_player_trueskill import update_ratings


def test_unsurprising_p1_win():
    p1_rating = Rating(mean=10, stddev=0.1)
    p2_rating = Rating(mean=2, stddev=0.1)
    outcome = 1
    new_p1, new_p2 = update_ratings(p1_rating, p2_rating, outcome)
    assert new_p1.mean > p1_rating.mean > p2_rating.mean > new_p2.mean


def test_surprising_p1_win():
    p1_rating = Rating(mean=2, stddev=0.1)
    p2_rating = Rating(mean=10, stddev=0.1)
    outcome = 1
    new_p1, new_p2 = update_ratings(p1_rating, p2_rating, outcome)

    # enough to change p2's rating to be lower than P1's old rating
    assert new_p2.mean < p1_rating.mean < new_p1.mean < p2_rating.mean

    # now we're more uncertain about both ratings due to the upset
    assert new_p1.stddev > p1_rating.stddev
    assert new_p2.stddev > p2_rating.stddev


def test_unsurprising_p1_loss():
    p1_rating = Rating(mean=2, stddev=0.1)
    p2_rating = Rating(mean=10, stddev=0.1)
    outcome = -1
    new_p1, new_p2 = update_ratings(p1_rating, p2_rating, outcome)
    assert new_p1.mean < p1_rating.mean
    assert new_p2.mean > p2_rating.mean


def test_surprising_p1_loss():
    p1_rating = Rating(mean=10, stddev=0.1)
    p2_rating = Rating(mean=2, stddev=0.1)
    outcome = -1
    new_p1, new_p2 = update_ratings(p1_rating, p2_rating, outcome)

    # enough to change p2's rating to be lower than P1's old rating
    assert new_p1.mean < p2_rating.mean < new_p2.mean < p1_rating.mean

    # now we're more uncertain about both ratings due to the upset
    assert new_p1.stddev > p1_rating.stddev
    assert new_p2.stddev > p2_rating.stddev
