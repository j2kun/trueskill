'''Types used for all impls.'''
from typing import Dict
from typing import NewType

from dataclasses import dataclass

from constants import DEFAULT_MEAN
from constants import DEFAULT_STD_DEV


# players are globally unique integer ids
Player = NewType('Player', int)


@dataclass(frozen=True)
class Rating:
    mean: float = DEFAULT_MEAN
    stddev: float = DEFAULT_STD_DEV


@dataclass(frozen=True)
class Team:
    # A team may have one or more players
    ratings: Dict[Player, Rating]
