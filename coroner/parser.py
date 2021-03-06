import traceback
from collections import defaultdict

from coroner_exceptions import *
import chunk_parsers
from chunk_parsers import get_parser_stable


# TODO: document this new modular structure
# TODO: Rename either this or the module. Or both.
class Morgue(object):
    # Keep track of seen bots so we can save them to a file at the end for later use
    bots = set()
    def __init__(self, f, intercept_exceptions=True):
        self.f = f
        self.game_row = {}
        # This is for tables that have 0-to-many rows per game
        self.ancillary_rows = defaultdict(list)
        self.name = None # player name
        if not intercept_exceptions:
            self.parse()
            return
        try:
            self.parse()
        except Exception as e:
            # TODO: This interception of exceptions is kind of awkward. There's
            # some finagling in parse.py to recover and print the trace of the
            # original intercepted error, but in the context of e.g. tests, we
            # end up with uninformative traces.
            e.fname = self.f.name
            e.version = self.game_row.get('version', 'UNK')
            # Unfortunately, it seems like the original line number gets lost
            # when reraising. This seems like a hack. Is there no better way?
            e.trace = traceback.format_exc(e)
            raise e

    def parse(self):
        parser_stable = get_parser_stable()
        while not parser_stable.done:
            try:
                chunk = self.next_chunk()
            except ChunkExhaustionException as e:
                parser_stable.check_satisfaction()
                # If the above check didn't raise an exception, then our parsers
                # were basically done (i.e. the only remaining unactivated ones
                # were marked as optional)
                return
                
            for k, v in parser_stable.parse_chunk(chunk, self):
                # Parsers may yield a (str, dict) tuple, where the key
                # is the name of an ancillary table, and the value is
                # the dict representation of a whole row for that table
                if isinstance(v, dict):
                    self.addrow(v, k)
                # The default behaviour is to yield a (column, scalar) tuple
                # corresponding to a column in the main games table
                else:
                    col, value = k, v
                    self.setcol(col, value)


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

