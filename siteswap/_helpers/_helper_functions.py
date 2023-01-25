from scipy.sparse import csr_matrix
import numpy as np

__all__ = ['adjacency_matrix', 'divisors', 'mobius']

# returns a sparse scipy matrix instead of the usual numpy array
def adjacency_matrix(balls: int, max_throw: int) -> np.ndarray:
    states = list(_multiset_permutations([1] * balls + [0] * (max_throw - balls)))
    rows = []
    cols = []

    for i, state in enumerate(states):
        a = state[1:] + [state[0]]

        j = _binary_search(a, states)

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

                j = _binary_search(a, states)

                rows.append(i)
                cols.append(j)

    data = np.ones(len(rows), dtype=int)

    return csr_matrix((data, (rows, cols)))

# based on the remainder check in
# https://en.wikipedia.org/wiki/Siteswap#Validity
def _balls_dont_collide(sequence: list[int]) -> bool:
    period = len(sequence)
    taken = [False] * period

    for i, x in enumerate(sequence):
        check = (x+i) % period
        if taken[check]:
            return False
        taken[check] = True
    return True

def _binary_search(x: int, a: list[list[int]]) -> int:
    m = 0
    n = len(a)

    # check sort order
    if len(a) > 1 and a[0] > a[1]:
        m, n = n, m

    while True:
        i = (m+n) // 2

        if a[i] == x:
            return i
        elif a[i] < x:
            m = i
        else:
            n = i

def divisors(n: int) -> list[int]:
    return [x for x in range(1, n+1) if n % x == 0]

# https://en.wikipedia.org/wiki/M%C3%B6bius_function
def mobius(n: int) -> int:
    if not isinstance(n, int) or n < 1:
        raise ValueError('mobius function works only with positive integers!')

    p = _prime_factors(n)

    for x in p:
        if n % (x*x) == 0:
            return 0

    if len(p) % 2 == 0:
        return 1
    else:
        return -1

def _multiset_permutations(a: list[int]) -> list[list[int]]:
    a = sorted(a, reverse=True)

    yield(a.copy())

    n = len(a)
    i = n - 2

    while True:
        for i in range(len(a) - 2, -2, -1):
            if a[i] > a[i+1]:
                j = i + 1
                break

        if i < 0:
            break

        a[i], a[j] = a[j], a[i]
        a[j+1:] = reversed(a[j+1:])

        yield a.copy()

def _prime_factors(n: int) -> list[int]:
    i = 2
    factors = []
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
            factors.append(i)
    if n > 1:
        factors.append(n)
    return factors

# 441 is the same siteswap as 414 and 144
# prefer the notation with the biggest number
def _sort_sequence(sequence: list[int]) -> list[int]:
    permutations = [sequence[i:] + sequence[:i] for i in range(len(sequence))]
    return max(permutations)

# amazing algorithm
# https://stackoverflow.com/a/29489919
def _substring_is_periodic(s: str) -> bool:
    if len(s) == 1:
        return False
    return (s+s).find(s, 1, -1) != -1
