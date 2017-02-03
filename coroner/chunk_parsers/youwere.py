import re

from base import ChunkParser
from ..coroner_exceptions import *
from .. import crawl_data


class YouWereParser(ChunkParser):
    order = 3
    shy = True
    @staticmethod
    def interested(chunk):
        # Does this have 1.0 precision and recall?
        # TODO: after doing a round of parsing, verify that the only games
        # where hunger is NaN are vampires
        return chunk[0].startswith('you ')

    @staticmethod
    def _parse(chunk):
        for line in chunk:
            if line in crawl_data.HUNGER_LINES:
                yield 'hunger', crawl_data.HUNGER_LINES[line]
