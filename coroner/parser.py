import traceback
from collections import defaultdict

from coroner_exceptions import *
import chunk_parsers
from chunk_parsers import PARSERS


# TODO: document this new modular structure
# TODO: Rename either this or the module. Or both.
class Morgue(object):
    # Keep track of seen bots so we can save them to a file at the end for later use
    bots = set()
    def __init__(self, f):
        self.f = f
        self.game_row = {}
        # This is for tables that have 0-to-many rows per game
        self.ancillary_rows = defaultdict(list)
        self.name = None # player name
        self.unactivated_parser_indices = range(len(PARSERS))
        try:
            self.parse()
        except Exception as e:
            e.fname = self.f.name
            e.version = self.game_row.get('version', 'UNK')
            # Unfortunately, it seems like the original line number gets lost
            # when reraising. This seems like a hack. Is there no better way?
            e.trace = traceback.format_exc(e)
            raise e

    def next_parsers(self):
        return [PARSERS[i] for i in self.unactivated_parser_indices[:3]]

    def mark_parser_done(self, parser):
        i = PARSERS.index(parser)
        self.unactivated_parser_indices.remove(i)

    def parse(self):
        # TODO: there's a lot more subtlety that could be added here:
        # - we should probably regard it as an error if certain pairs of parsers
        #   are woken up out of order
        # - we should probably bail early if we go through a drought of more than
        #   n chunks without satisfying parser x. (Though this probably has a pretty
        #   negligible effect on perf, since morgues that fail to activate all
        #   parsers should be a tiny minority. For all the others, we're already
        #   going through all the chunks.)
        while self.unactivated_parser_indices:
            try:
                chunk = self.next_chunk()
            except ChunkExhaustionException as e:
                # Filter out optional parsers
                dormant = {PARSERS[i].__name__ for i in self.unactivated_parser_indices
                        if not PARSERS[i].optional
                }
                if not dormant:
                    break
                # It happens pretty often that we can't find these. nbd.
                often_missing = {'BranchParser', 'NotesParser'}
                if dormant.issubset(often_missing):
                    kls = MissingChunkException
                else:
                    kls = CritMissingChunkException
                raise kls(dormant)

            for parser in self.next_parsers():
                if not parser.interested(chunk):
                    continue
                didsomething = False
                for (col, value) in parser.parse(chunk, self):
                    didsomething = True
                    self.setcol(col, value)
                if didsomething or parser.shy:
                    self.mark_parser_done(parser)
                    # This chunk was consumed, so we can move on to the next
                    break
                else:
                    raise ParseException("Parser {} was interested but produced no output".format(parser))

    def setcol(self, col, value, table='game'):
        dest = self.game_row if table == 'game' else self.ancillary_rows[table]
        dest[col] = value

    def addrow(self, rowdict, table):
        self.ancillary_rows[table].append(rowdict)

    def next_chunk(self):
        """Return the next "chunk" in this morgue file - i.e. the next non-blank
        line and all lines after it until the next blank line - as a list of strings 
        (which we strip and lowercase before returning)"""
        chunk = []
        while 1:
            line = self.f.readline()
            # Have we exhausted the file?
            if line == '':
                if chunk:
                    return chunk
                else:
                    raise ChunkExhaustionException()
            if line == '\n':
                # The last call read until it encountered a blank line. But
                # sometimes there's more than one consecutive blank line, which
                # we need to power through before getting to the good stuff
                if len(chunk) == 0:
                    continue
                else:
                    break
            chunk.append(line.strip().lower())
        return chunk

