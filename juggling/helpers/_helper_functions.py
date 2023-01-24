from scipy.sparse import csr_matrix
from ._util_functions import (
    binary_search,
    multiset_permutations
)
import numpy as np

# returns a sparse scipy matrix instead of the usual numpy array
def adjacency_matrix(balls: int, max_throw: int) -> np.ndarray:
    states = list(multiset_permutations([1] * balls + [0] * (max_throw - balls)))
    rows = []
    cols = []

    for i, state in enumerate(states):
        a = state[1:] + [state[0]]

        j = binary_search(a, states)

        rows.append(i)
        cols.append(j)

        if state[0] == 1:
            k = max_throw - 2
            l = max_throw - 1

            for _ in range(max_throw - balls):
                while a[k] == a[l]:
                    k -= 1
                    
                a[k], a[l] = a[l], a[k]
                l = k

                j = binary_search(a, states)

                rows.append(i)
                cols.append(j)

    data = np.ones(len(rows), dtype=int)

    return csr_matrix((data, (rows, cols)))

# based on the remainder check in
# https://en.wikipedia.org/wiki/Siteswap#Validity
def balls_dont_collide(sequence: list[int]) -> bool:
    period = len(sequence)
    taken = [False] * period

    for i, x in enumerate(sequence):
        check = (x+i) % period
        if taken[check]:
            return False
        taken[check] = True
    return True

# jugglinglab.org siteswap notation
# numbers 0-9 are mapped to their string representations
# numbers 10-35 are mapped to a-z
def int_to_siteswap(n: int) -> str:
    if n < 0 or n > 35:
        raise ValueError('Cannot convert to siteswap notation! Number must be between [0, 35]')
    return '0123456789abcdefghijklmnopqrstuvwxyz'[n]

def siteswap_to_int(s: str) -> int:
    return int(s, 36)

# 441 is the same siteswap as 414 and 144
# prefer the notation with the biggest number
def sort_sequence(sequence: list[int]) -> list[int]:
    permutations = [sequence[i:] + sequence[:i] for i in range(len(sequence))]
    return max(permutations)
