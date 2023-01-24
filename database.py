from _db_constants import (
    BYTES_PER_PATTERN,
    CHUNK_SIZE,
    HEADER_SIZE,
)
from _util_functions import (
    decode_hex,
    decode_int,
    encode_hex,
    encode_int32,
    encode_int64,
    patterns_to_printable_filesize,
)
import json

__all__ == 'SiteswapDB'

class SiteswapFileException(Exception):
    pass

class SiteswapDB():
    # def __getitem__(self, i) -> dict[int, list[str]]:
    #     return None
    #     # return self.read_file(f'db/{i}balls.bin')

    def _create_header(self, balls: int, max_throw: int, patterns: dict[int, int] = None) -> bytes:
        """
        Creates a header for a siteswap file.

        :param   balls:      how many juggling balls
        :param   max_throw:  maximum throw of a siteswap
        :param   patterns:   dictionary with period as key, number of patterns as value
        :raises  ValueError: if arguments are not valid
        :returns a bytearray
        """
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

        if max_throw < 1:
            raise ValueError('maximum throw must be greater than 0!')

        # 8 bytes for file signature
        header = bytearray(b'SITESWAP')

        # 4 bytes for number of balls
        header += encode_int32(balls)

        # 4 bytes for max_throw
        header += encode_int32(max_throw)

        # 16 x 8 bytes = 128 bytes for number of patterns per period
        for i in range(1, 17):
            header += encode_int64(patterns[i])

        # 16 bytes of only 'f'
        header += encode_hex('f' * 32)

        # a total of HEADER_SIZE=160 bytes
        return header

    def _read_header(self, b: bytes) -> tuple[int, int, dict[int, int]]:
        """
        Reads the header of a siteswap file.

        :param   b:                     bytes making up the header
        :raises  SiteswapFileException: if header is not valid
        :returns a tuple of (balls, max_throw, patterns)
        """
        self._validate_header(b)

        balls = decode_int(b[8:16])
        max_throw = decode_int(b[12:16])
        patterns = {i: decode_int(b[8+i*8:16+i*8]) for i in range(1, 17)}

        return balls, max_throw, patterns

    def _update_header(self, filename: str, new_patterns: dict[int, int]) -> None:
        """
        Updates the header of a siteswap file.

        :param filename:     a filename
        :param new_patterns: dictionary with period as key, number of patterns as value
        :raises Error:       if file could not be read
        """
        try:
            with open(filename, 'r+b') as f:
                # get the old header
                balls, max_throw, patterns = self._read_header(f.read(HEADER_SIZE))

                patterns.update(new_patterns)

                new_header = _create_header(balls, max_throw, patterns)

                f.seek(0)
                f.write(new_header)
        except (FileNotFoundError, IsADirectoryError, PermissionError, OSError) as e:
            print(e)

    def _validate_header(self, b: bytes) -> None:
        """
        Validates a header. Performs the following tests:
        
        1) header size is HEADER_SIZE
        2) file signature exists
        3) end of header exists

        :param b:                      bytes making up the header
        :raises SiteswapFileException: if header is not valid
        """
        if len(b) != HEADER_SIZE:
            raise SiteswapFileException(f'Expecting {HEADER_SIZE} bytes when reading header!')

        signature = b[:8]

        if signature != b'SITESWAP':
            print(signature)
            raise SiteswapFileException('File signature missing from header!')

        end_of_header = b[-16:]

        if decode_hex(end_of_header) != 'f' * 32:
            raise SiteswapFileException('End of header missing from header!')

    def get_siteswap(self, i: int, balls: int, period: int) -> str:
        """
        Fetches a single siteswap with index i, balls b and period n from a siteswap file.
        
        Index i is calculated from where the patterns with this period starts.
        For example, lets say there's two patterns with b=2, n=2, namely '31' and '40'. Then:
            get_siteswap(0, 2, 2) => '31'
            get_siteswap(1, 2, 2) => '40'
            get_siteswap(2, 2, 2) => IndexError

        :param i:                      index of the siteswap pattern
        :param balls:                  number of balls in the siteswap pattern
        :param period:                 the period of the siteswap pattern
        :returns                       a string (the siteswap)
        :raises IndexError:            if index is not in db
        :raises Error:                 if file could not be read
        :raises SiteswapFileException: if period of fetched siteswap is wrong, meaning that header and data don't match
        """
        try:
            with open(f'db/{balls}balls.bin', 'rb') as f:
                _, _, patterns = self._read_header(f.read(HEADER_SIZE))

                period_start = sum(list(patterns.values())[:period-1])
                period_end = sum(list(patterns.values())[:period])

                if (i > patterns[period] or
                    i + period_start >= period_end):
                    # don't have it in database
                    raise IndexError('Index out of range')

                # calculate the offset where to read data from
                offset = HEADER_SIZE + (period_start + i) * BYTES_PER_PATTERN

                f.seek(offset)

                siteswap = decode_hex(f.read(8))

                if len(siteswap) != period:
                    raise SiteswapFileException('Period of fetched siteswap is wrong. Header and data mismatch.')

                return siteswap
        except (FileNotFoundError, IsADirectoryError, PermissionError, OSError) as e:
            print(e)

    def get_siteswaps(self, balls: int, period: int) -> list[str]:
        """
        Fetches all siteswaps with balls b and period n from a siteswap file.
        
        For example:
            get_siteswaps(2, 2) => ['31', '40']

        :param balls:  number of balls in the siteswap pattern
        :param period: the period of the siteswap pattern
        :returns       a list of siteswaps
        :raises Error: if file could not be read
        """
        try:
            with open(f'db/{balls}balls.bin', 'rb') as f:
                _, _, patterns = self._read_header(f.read(HEADER_SIZE))

                period_start = sum(list(patterns.values())[:period-1])
                period_end = sum(list(patterns.values())[:period])

                offset = HEADER_SIZE + period_start * BYTES_PER_PATTERN

                f.seek(offset)

                chunk = f.read((period_end - period_start) * BYTES_PER_PATTERN)

                first_siteswap = decode_hex(chunk[:8])
                last_siteswap = decode_hex(chunk[-8:])

                if (len(first_siteswap) != period or
                    len(last_siteswap) != period):
                    # raise an exception
                    raise SiteswapFileException('Period of fetched siteswaps is wrong. Header and data mismatch.')

                return [decode_hex(chunk[i:i+8]) for i in range(0, len(chunk), 8)]
        except (FileNotFoundError, IsADirectoryError, PermissionError, OSError) as e:
            print(e)

    # # TO-DO: patterns to key db.patterns[b][p]
    # @property
    # def patterns(self, i) -> dict[dict[int, list[str]]]:
    #     return self.read_file(f'db/{i}balls.bin')

    def print_info(self, filename: str) -> None:
        """
        Prints information about a siteswap file.

        :param  filename: a filename
        :raises Error:    if file could not be read
        """
        try:
            with open(filename, 'rb') as f:
                balls, max_throw, patterns = self._read_header(f.read(HEADER_SIZE))

            print(f"\nSiteswap database file '{filename}'")
            print(f"{balls} ball{'' if balls == 1 else 's'} with max_throw {max_throw}\n")

            p = 0
            for k, v in patterns.items():
                p += v
                print(f"Period {k}:\t{v} pattern{'' if v == 1 else 's'}")

            print(f"\nTotal: {p} pattern{'' if p == 1 else 's'}. File size on disk: {patterns_to_printable_filesize(p)}")
        except (FileNotFoundError, IsADirectoryError, PermissionError, OSError) as e:
            print(e)

    def read_file(self, filename: str) -> dict[int, list[str]]:
        """
        Completely reads a siteswap file and returns the patterns inside.

        :param         filename: a filename
        :returns       a dictionary with period as key, list of patterns as value
        :raises Error: if file could not be read
        """
        d = {i: [] for i in range(1, 17)}

        try:
            with open(filename, 'rb') as f:
                # check that the header is all right
                self._validate_header(f.read(HEADER_SIZE))

                while chunk := f.read(CHUNK_SIZE):
                    mem_view = memoryview(chunk)
                    gen = (decode_hex(mem_view[i:i+8]) for i in range(0, len(mem_view), 8))
                    for s in gen:
                        d[len(s)].append(s)
            return d
        except (FileNotFoundError, IsADirectoryError, PermissionError, OSError) as e:
            print(e)
