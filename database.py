from _db_constants import (
    BYTES_PER_PATTERN,
    CHUNK_SIZE,
    HEADER_SIZE,
)

from _util_functions import (
    decode_hex,
    decode_int64,
    encode_hex,
    encode_int64,
    patterns_to_printable_filesize,
)

# from siteswap import number_of_juggling_patterns

import json

class SiteswapFileException(Exception):
    pass

# def calculate_disk_space(balls, period, max_throw):
#     patterns = 0

#     for p in range(1, period+1):
#         patterns += number_of_juggling_patterns(balls, period, max_throw)

#     bytes_per_pattern = 8

#     if patterns >= 1e12 // bytes_per_pattern:
#         print(f'{balls} balls up to a period of {period} takes {patterns*8e-9:.2f} TB of disk space')
#     elif patterns >= 1e9 // bytes_per_pattern:
#         print(f'{balls} balls up to a period of {period} takes {patterns*8e-9:.2f} GB of disk space')
#     elif patterns >= 1e6 // bytes_per_pattern:
#         print(f'{balls} balls up to a period of {period} takes {patterns*8e-6:.2f} MB of disk space')
#     else:
#         print(f'{balls} balls up to a period of {period} takes {patterns*8e-3:.2f} KB of disk space')

def create_header(balls: int, patterns: dict[int, int] = None) -> bytes:
    if not patterns:
        patterns = {i: 0 for i in range(1, 17)}

    # fill in missing patterns
    for i in range(1, 17):
        try:
            patterns[i]
        except KeyError:
            patterns[i] = 0

    if len(patterns) > 16:
        raise ValueError('patterns supports only keys between 1-16!')

    if balls < 1:
        raise ValueError('number of balls must be greater than 0!')

    # 8 bytes for file signature
    header = bytearray(b'SITESWAP')

    # 8 bytes for number of balls
    header += encode_int64(balls)

    # 16 x 8 bytes = 128 bytes for number of patterns per period
    for i in range(1, 17):
        header += encode_int64(patterns[i])

    # 16 bytes of only 'f'
    header += encode_hex('f' * 32)

    # a total of HEADER_SIZE=160 bytes
    return header

def get_header(b: bytes) -> tuple[int, dict[int, int]]:
    validate_header(b)

    balls = decode_int64(b[8:16])
    patterns = {i: decode_int64(b[8+i*8:16+i*8]) for i in range(1, 17)}

    return balls, patterns

def get_siteswap(i: int, balls: int, period: int) -> str:
    with open(f'db/{balls}balls.bin', 'rb') as f:
        _, patterns = get_header(f.read(HEADER_SIZE))

        if i > patterns[period]:
            # don't have it in database
            return
        
        # offset in patterns
        patterns_start = sum(list(patterns.values())[:period-1])
        
        offset = HEADER_SIZE + (patterns_start + i) * BYTES_PER_PATTERN

        f.seek(offset)

        return decode_hex(f.read(8))

def print_info(filename: str) -> None:
    with open(filename, 'rb') as f:
        balls, patterns = get_header(f.read(HEADER_SIZE))

    print(f"Siteswap database file '{filename}'")
    print(f"{balls} ball{'' if balls == 1 else 's'}\n")

    p = 0
    for k, v in patterns.items():
        p += v
        print(f"Period {k}:\t{v} pattern{'' if v == 1 else 's'}")

    print(f"\nTotal: {p} pattern{'' if p == 1 else 's'}. File size on disk: {patterns_to_printable_filesize(p)}")

def read_file(filename: str) -> dict[int, list[str]]:
    d = {i: [] for i in range(1, 17)}
    with open(filename, 'rb') as f:
        # check that the header is all right
        validate_header(f.read(HEADER_SIZE))

        while chunk := f.read(CHUNK_SIZE):
            mem_view = memoryview(chunk).hex()
            gen = (mem_view[i:i+16].lstrip('0') for i in range(0, len(mem_view), 16))
            for s in gen:
                d[len(s)].append(s)
    return d

def update_header(filename: str, new_patterns: dict[int, int]) -> None:
    with open(f'{filename}', 'r+b') as f:
        # get the old header
        balls, patterns = get_header(f.read(HEADER_SIZE))

        patterns.update(new_patterns)

        new_header = create_header(balls, patterns)

        f.seek(0)
        f.write(new_header)

def validate_header(b: bytes) -> None:
    if len(b) != HEADER_SIZE:
        raise SiteswapFileException(f'Expecting {HEADER_SIZE} bytes when reading header!')

    signature = b[:8]

    if signature != b'SITESWAP':
        print(signature)
        raise SiteswapFileException('File signature missing from header!')

    end_of_header = b[-16:]

    if decode_hex(end_of_header) != 'f' * 32:
        raise SiteswapFileException('End of header missing from header!')

# if __name__ == '__main__':
#     max_throw = 12
#     balls = 9

#     for period in range(13, 14):
#         siteswaps = all_siteswaps(period, balls, max_throw)
    
#         with open(f'db/{balls}balls.bin', 'ab') as f:
#             header = create_header(balls)
#             for s in siteswaps:
#                 f.write(encode_hex(s))
#         print(f'{balls} balls period {period} DONE')
