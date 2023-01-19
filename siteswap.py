from _helper_functions import adjacency_matrix
from _siteswap_cython import all_siteswaps_between
from _util_functions import (
    divisors,
    mobius,
)

from multiprocessing import Pool
from random import randrange
import database
import json
import numpy as np

def all_siteswaps(balls: int, period: int, max_throw: int) -> list[str]:
    if not validate_siteswap(balls, period, max_throw):
        return []

    s = set()
    
    with Pool() as p:
        for i in range(balls, max_throw+1):
            p.apply_async(
                all_siteswaps_between,
                (period, balls, max_throw, i, i+1),
                callback=s.update
            )
        p.close()
        p.join()
     
    return sorted(s, key=lambda item: (len(item), item))

def number_of_juggling_patterns(balls: int, period: int, max_throw: int = None) -> int:
    if balls < 1 or period < 1:
        return 0

    if not max_throw or max_throw >= balls * period:
        # max_throw is infinity, but in practice it's limited to balls * period
        # in a juggling pattern of minimal period n
        return int(sum(mobius(period // d) * ((balls+1)**d - balls**d) for d in divisors(period)) // period)

    if max_throw < balls:
        return 0

    M = adjacency_matrix(balls, max_throw)

    return int(sum(mobius(period // d) * np.sum((M ** d).diagonal()) for d in divisors(period)) // period)

def random_siteswap(balls: int, period: int, max_throw: int) -> str:
    validate_siteswap(balls, period, max_throw)
    
    with open('db/patterns.json', 'r') as f:
        patterns = json.load(f)

    N = patterns[balls-1][period-1][max_throw-1]

    random_number = randrange(0, N)

    siteswap = database.get_siteswap(random_number, balls, period)

    return siteswap

def validate_siteswap(balls: int, period: int, max_throw: int) -> None:
    if max_throw > 15:
        raise ValueError('maximum throw must be less than 16!')

    if balls < 1:
        raise ValueError('balls must be at least 1!')

    if period < 1:
        raise ValueError('period must be at least 1!')

    if max_throw < balls:
        raise ValueError('maximum throw must be at least the number of balls!')

    return True

if __name__ == '__main__':
    print(all_siteswaps(4, 5, 9))
