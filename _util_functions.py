from _db_constants import BYTES_PER_PATTERN, HEADER_SIZE

def binary_search(x: int, a: list[list[int]]) -> int:
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

def decode_hex(b: bytes) -> str:
    return b.hex().lstrip('0')

def decode_int64(b: bytes) -> int:
    return int.from_bytes(b, byteorder='big', signed=False)

def divisors(n: int) -> list[int]:
    return [x for x in range(1, n+1) if n % x == 0]

def encode_hex(s: str) -> bytes:
    return bytes.fromhex('0' * (16-len(s)) + s)

def encode_int64(i: int) -> bytes:
    return (i).to_bytes(8, byteorder='big', signed=False)

# https://en.wikipedia.org/wiki/M%C3%B6bius_function
def mobius(n: int) -> int:
    if not isinstance(n, int) or n < 1:
        raise ValueError('mobius function works only with positive integers!')

    p = prime_factors(n)

    for x in p:
        if n % (x*x) == 0:
            return 0

    if len(p) % 2 == 0:
        return 1
    else:
        return -1

def multiset_permutations(a: list[int]) -> list[list[int]]:
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

def patterns_to_printable_filesize(patterns: int) -> float:
    # Add the size of the header
    patterns += HEADER_SIZE // BYTES_PER_PATTERN

    if patterns >= 1e12 // BYTES_PER_PATTERN:
        patterns /= 1e12 // BYTES_PER_PATTERN
        return f'{patterns:.1f}'.rstrip('0').rstrip('.') + ' TB'
    elif patterns >= 1e9 // BYTES_PER_PATTERN:
        patterns /= 1e9 // BYTES_PER_PATTERN
        return f'{patterns:.1f}'.rstrip('0').rstrip('.') + ' GB'
    elif patterns >= 1e6 // BYTES_PER_PATTERN:
        patterns /= 1e6 // BYTES_PER_PATTERN
        return f'{patterns:.1f}'.rstrip('0').rstrip('.') + ' MB'
    elif patterns >= 1e3 // BYTES_PER_PATTERN:
        patterns /= 1e3 // BYTES_PER_PATTERN
        return f'{patterns:.1f}'.rstrip('0').rstrip('.') + ' KB'
    return f'{patterns*BYTES_PER_PATTERN} bytes'

def prime_factors(n: int) -> list[int]:
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

# amazing algorithm
# https://stackoverflow.com/a/29489919
def substring_is_periodic(s: str) -> bool:
    if len(s) == 1:
        return False
    return (s+s).find(s, 1, -1) != -1
