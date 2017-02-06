import re

from base import ChunkParser
from ..coroner_exceptions import *
from .. import crawl_data


class StatusParser(ChunkParser):
    shy = True
    @staticmethod
    def interested(chunk):
        return chunk[0].startswith('@: ')

    @staticmethod
    def _parse(chunk):
        for line in chunk:
            if line.startswith('0:'):
                assert 'orb of zot' in line, line
                yield 'orb', True
        
        
        
# Just dumping some old code from parse.py here in case I want to adapt it
# later when parsing statuses and stuff
"""

        # TODO: handle statuses
        while False and i < len(lines):
            line = lines[i]
            i += 1
            if line.startswith('}:'):
                # wrapping. This is gonna be a recurring problem.
                if line.endswith(','):
                    line += ' ' + lines[i]
                    i += 1
                match = re.match(r'}: (\d+)/15 runes: (.*)$', line)
                n, runestr = match.groups()
                self.setcol('nrunes', int(n))
                runes = [rune.strip() for rune in runestr.split(',')]
                for rune in runes:
                    assert rune, 'Got into a bad rune situation: {}'.format(lines)
                    self.setcol('rune_{}'.format(rune), True)
                break
"""
