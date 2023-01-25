from ._db_constants import BYTES_PER_PATTERN, HEADER_SIZE

__all__ = ['decode_hex', 'decode_int', 'encode_hex',
           'encode_int32', 'encode_int64', 'int_to_siteswap'
           'siteswap_to_int', 'patterns_to_printable_filesize']

def decode_hex(b: bytes) -> str:
    return b.hex().lstrip('0')

def decode_int(b: bytes) -> int:
    return int.from_bytes(b, byteorder='big', signed=False)

def encode_hex(s: str) -> bytes:
    return bytes.fromhex('0' * (16-len(s)) + s)

def encode_int32(i: int) -> bytes:
    return (i).to_bytes(4, byteorder='big', signed=False)

def encode_int64(i: int) -> bytes:
    return (i).to_bytes(8, byteorder='big', signed=False)

# jugglinglab.org siteswap notation
# numbers 0-9 are mapped to their string representations
# numbers 10-35 are mapped to a-z
def int_to_siteswap(n: int) -> str:
    if n < 0 or n > 35:
        raise ValueError('Cannot convert to siteswap notation! Number must be between [0, 35]')
    return '0123456789abcdefghijklmnopqrstuvwxyz'[n]

def siteswap_to_int(s: str) -> int:
    return int(s, 36)

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
