import re

from base import ChunkParser
from ..coroner_exceptions import *
from .. import crawl_data

class SkillProgressionTableParser(ChunkParser):
    """Parses the table, usually around the very bottom, mapping player level to
    skill level. Each (xl, skill_lvl) pair becomes a row in the 'skill_progression' table.

    These tables started to appear in morgues around version 18.x, so this parser is optional.
    """
    optional = True
    @staticmethod
    def interested(chunk):
        return re.match('skill\s+xl:', chunk[0])

    def _parse(self, chunk):
        # Ugh, this is gonna be a nightmare.
        header = chunk[0]
        col_headings_str = header.split('|')[1].strip()
        self.xls = map(int, col_headings_str.split())

        # Skip the first two lines (header, separator)
        for row in chunk[2:]:
            for thing in self._parse_row(row):
                yield thing

    def _parse_row(self, row):
        skill, lvls, total_ = row.split('|')
        skill = skill.strip()
        # Exactly 3 characters per column, either looking like "   ",
        # "  \d", or " \d\d".
        for i, xl in enumerate(self.xls):
            cell = lvls[3*i:3*(i+1)]
            if cell == '   ':
                continue
            skill_lvl = int(cell)
            yield 'skill_progression', dict(xl=xl, skill=skill, lvl=skill_lvl)
