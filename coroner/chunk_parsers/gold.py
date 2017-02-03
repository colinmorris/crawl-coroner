import re

from base import ChunkParser
from ..coroner_exceptions import *
from .. import crawl_data


class GoldParser(ChunkParser):
    optional = True
    @staticmethod
    def interested(chunk):
        # Saw some files where "a You visited X branches" line immediately 
        # preceded the gold stuff, but I think it might only be for sprint 
        # games.
        return chunk[0].startswith('you collected ')

    @staticmethod
    def _parse(chunk):
        m = re.match('you collected (\d+) gold pieces.', chunk[0])
        assert m, chunk[0]
        yield 'gold_collected', int(m.group(1))
        # Second line is how much you spent in shops.
        # May also be a third line: "You paid X gold pieces to Gozag"
        # In rare cases there may be no second line, which is why we
        # don't insist on a match below
        if len(chunk) > 1:
            m = re.match('you spent (\d+) gold', chunk[1])
            if m:
                yield 'gold_spent', int(m.group(1))

