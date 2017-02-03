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

# Ordered from approx beginning to end of file.
PARSERS = [
        FirstLineParser, SummaryParser, StatsTableParser, 
        # interchangeable?
        YouWereParser, YouVisitedParser, GoldParser, 
        # interchangeable?
        SkillsParser, BranchParser, NotesParser, 
]

# TODO: Need to define some strict ordering between groups of chunks.
# Not a big deal for now, but adding more parsers for optional chunks
# will quickly lead to problems as pile-ups of unsatisfied optional
# parsers form at the front of the line.

# TODO: It turns out there can be a LOT of variability in order in some cases.
# I'm seeing some cases where skills/branches come before youwere/youvisited/gold
