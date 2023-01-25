from ._helpers._helper_functions import adjacency_matrix
from ._helpers._siteswap_cython import all_siteswaps_between
from ._helpers._util_functions import (
    divisors,
    mobius,
)

from siteswap.database import SiteswapDB
from multiprocessing import Pool
from random import randrange
import json
import numpy as np

__all__ = ['all_siteswaps', 'number_of_juggling_patterns', 'random_siteswap']

def all_siteswaps(balls: int, period: int, max_throw: int = None) -> list[str]:
    if (not max_throw or max_throw > balls * period):
        max_throw = balls * period

    _validate_siteswap(balls, period, max_throw)

    s = []
    
    # parallelize searching for siteswaps
    with Pool() as p:
        for i in range(balls, max_throw+1):
            p.apply_async(
                all_siteswaps_between,
                (period, balls, max_throw, i, i+1),
                callback=s.extend
            )
        p.close()
        p.join()
     
    return sorted(s, key=lambda item: (len(item), item))

def number_of_juggling_patterns(balls: int, period: int, max_throw: int = None) -> int:
    if balls < 1 or period < 1:
        return 0

    if (not max_throw or max_throw >= balls * period):
        # max_throw is infinity, but in practice it's limited to balls * period
        # in a juggling pattern of minimal period n
        return int(sum(mobius(period // d) * ((balls+1)**d - balls**d) for d in divisors(period)) // period)

    if max_throw < balls:
        return 0

    M = adjacency_matrix(balls, max_throw)

    return int(sum(mobius(period // d) * np.sum((M ** d).diagonal()) for d in divisors(period)) // period)

def random_siteswap(balls: int, period: int, max_throw: int = None) -> str:
    if (not max_throw or max_throw > balls * period):
        max_throw = balls * period

    _validate_siteswap(balls, period, max_throw)
    
    with open('db/patterns.json', 'r') as f:
        patterns = json.load(f)

    N = patterns[balls-1][period-1][max_throw-1]

    random_number = randrange(0, N)

    siteswap = SiteswapDB().get_siteswap(random_number, balls, period)

    return siteswap

def _validate_siteswap(balls: int, period: int, max_throw: int) -> None:
    if max_throw > 35:
        raise ValueError('maximum throw must be less than 36!')

    if balls < 1:
        raise ValueError('balls must be at least 1!')

    if period < 1:
        raise ValueError('period must be at least 1!')

    if max_throw < balls:
        raise ValueError('maximum throw must be at least the number of balls!')
