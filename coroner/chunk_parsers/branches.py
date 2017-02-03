import re

from base import ChunkParser
from ..coroner_exceptions import *
from .. import crawl_data


class BranchParser(ChunkParser):
    order = 6
    shy = True
    @staticmethod
    def interested(chunk):
        return chunk[0] == 'branches:'

    @staticmethod
    def _parse(chunk):
        blob = ' '.join(chunk[1:])
        tokens = blob.split()
        i = 0
        # Looking around for substrings like 'Temple (1/1) D:7'
        while i < len(tokens):
            w = tokens[i]
            i += 1
            if w not in crawl_data.BRANCHES:
                continue
            branch = w
            w = tokens[i]
            i += 1
            # I think this indicates the player has at least seen the entrance
            # I think (0/X) means they haven't entered it. If they've been to
            # the range of levels where it should appear, but haven't seen the
            # entrance, they get something like 'Vaults: D:13-D14'
            if w[0] == '(':
                yield 'saw_'+branch, True

