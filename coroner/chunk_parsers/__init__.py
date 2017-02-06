# This is annoyingly tedious. Could maybe solve it with some decorator magic, but whatever.
from summary import SummaryParser
from firstline import FirstLineParser
from branches import BranchParser
from notes import NotesParser
from skills import SkillsParser
from stats_table import StatsTableParser
from youvisited import YouVisitedParser
from youwere import YouWereParser
from gold import GoldParser

from parser_stable import ChunkParserStable

# Ordered by strict precedence. If group A comes before group B, then no parser
# in A may be activated after any parser in B. Within a group, parsers can 
# activate in arbitrary order.
_PARSERS = [
        [FirstLineParser], 
        [SummaryParser], 
        [StatsTableParser], 
        [SkillsParser, BranchParser, YouWereParser, YouVisitedParser, GoldParser,],
        [NotesParser], 
]

def get_parser_stable():
    return ChunkParserStable(_PARSERS)

__all__ = [get_parser_stable]

