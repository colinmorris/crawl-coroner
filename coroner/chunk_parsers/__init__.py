from summary import SummaryParser
from firstline import FirstLineParser

parsers = [SummaryParser, FirstLineParser]

parsers.sort(key=lambda parser: parser.order)
