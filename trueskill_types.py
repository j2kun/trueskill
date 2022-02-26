'''Types used for all impls.'''
from dataclasses import dataclass

from constants import DEFAULT_MEAN
from constants import DEFAULT_STD_DEV


@dataclass(frozen=True)
class Rating:
    mean: float = DEFAULT_MEAN
    stddev: float = DEFAULT_STD_DEV
