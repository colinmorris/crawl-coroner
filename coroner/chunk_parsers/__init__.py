# This is annoyingly tedious. Could maybe solve it with some decorator magic, but whatever.
from summary import SummaryParser
from firstline import FirstLineParser
from branches import BranchParser
from notes import NotesParser
from skills import SkillsParser
from stats_table import StatsTableParser
from youvisited import YouVisitedParser
from youwere import YouWereParser

PARSERS = [SummaryParser, FirstLineParser, BranchParser, NotesParser, SkillsParser,
        StatsTableParser, YouVisitedParser, YouWereParser]

PARSERS.sort(key=lambda parser: parser.order)
# Order:
#   firstline, summary, stats_table youwere, youvisited, skills, branches, notes
