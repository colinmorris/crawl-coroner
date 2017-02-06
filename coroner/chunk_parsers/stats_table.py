import re

from base import ChunkParser
from ..coroner_exceptions import *
from .. import crawl_data


class StatsTableParser(ChunkParser):
    @staticmethod
    def interested(chunk):
        prefix_pattern = '(?:health:|hp:?) +-?\d'
        return re.match(prefix_pattern, chunk[0])

    @staticmethod
    def _parse(lines):
        hpline = lines[0]
        hp_pattern = '(?:health:|hp:?) +(-?\d+)/(\d+)'
        m = re.match(hp_pattern, hpline)
        assert m, "Couldn't find current/max hp in line:\n{}".format(hpline)
        hp, maxhp = map(int, m.groups())
        yield 'hp', hp
        yield 'maxhp', maxhp
        # TODO: A common variety of parsing error comes from values that look like "God: $foo \d\d". Should be easy to handle.
        godline = lines[1]
        parts = godline.split()
        try:
            gindex = parts.index('god:') + 1
        # Weird spacing issues with big stats?
        except ValueError:
            for i, part in enumerate(parts):
                if 'god:' in part:
                    gindex = i + 1
                    break
            else:
                raise Exception('Weird line: ' + godline)
        if gindex == len(parts):
            # there is no god
            god = 'none'
        # Xom formatting is a bit wonky
        elif parts[gindex] in ('xom', '*xom'):
            god = 'xom'
        elif gindex == len(parts) - 1: # Special case for gozag, who doesn't have piety
            god = parts[gindex]
        else:
            god = ' '.join(parts[gindex:-1])
            assert god, godline
        # Sometimes we'll get a string like '*Zin', meaning worshipping Zin but under penance
        if god[0] == '*':
            god = ' '.join(parts[gindex:])[1:]
        # Canonicalize ukayaw, dithmengos
        god = crawl_data.RENAMED_GODS.get(god, god)
        assert god == 'none' or god in crawl_data.GODS, 'Unrecognized god: {}'.format(god)
        yield 'god', god

