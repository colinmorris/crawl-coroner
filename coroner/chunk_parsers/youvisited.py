import re

from base import ChunkParser
from ..coroner_exceptions import *
from .. import crawl_data


class YouVisitedParser(ChunkParser):
    order = 4
    shy = True
    @staticmethod
    def interested(chunk):
        return chunk[0].startswith('you visited')

    @staticmethod
    def _parse(visited):
        for line in visited:
            prefix = 'you also visited: '
            if not line.startswith(prefix):
                continue
            # Skip the last char, which is a period.
            portalstr = line[len(prefix):-1].replace(' and', ',')
            portals = portalstr.split(', ')
            for portal in portals:
                try:
                    # Sometimes get stuff like 'labyrinth (2 times)'
                    # TODO: this is probably information I should record for the
                    # purposes of some analyses, though I think it's a pretty 
                    # rare phenomenon (is it even possible to get 2 of the same 
                    # portal vault in one game in the current version?)
                    paren = portal.index('(')
                    portal = portal[:paren]
                except ValueError:
                    pass
                yield 'visited_'+portal.strip(), True

