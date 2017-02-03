import re

from base import ChunkParser
from ..coroner_exceptions import *
from .. import crawl_data


class SkillsParser(ChunkParser):
    order = 5
    @staticmethod
    def interested(chunk):
        return chunk[0] == 'skills:'

    @staticmethod
    def _parse(chunk):
        for skill_line in chunk[1:]:
            match = re.search('level (\d+\.?\d?)', skill_line)
            assert match, skill_line
            lvl = float(match.group(1))
            skill_start = 2
            parts = skill_line.split()
            while not parts[skill_start].isalpha():
                skill_start += 1
            skill_name = ' '.join(parts[skill_start:])
            assert skill_name, skill_line
            yield 'skill_'+skill_name, lvl
