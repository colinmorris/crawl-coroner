import re
from collections import namedtuple

from base import ChunkParser
from ..coroner_exceptions import *
from .. import crawl_data


Note = namedtuple('Note', 'text place turn')

# TODO (micro-optimization): we could be a little more efficient by allowing a 
# parser to say:
#   - this was the kind of note I'm interested in (and therefore none of the
#   other parsers are going to be interested, so you can break now)
#   - I'm done. Don't call me again. 

# It'd be kind of nice to have this be a class variable of NotesParser, but that
# seems not to be possible? I guess because at the time the decorator is called,
# NotesParser isn't defined yet (we're in the process of putting it together)
_NOTEPARSERS = set()
def noteparser(fn):
    global _NOTEPARSERS
    _NOTEPARSERS.add(fn)
    return fn

class NotesParser(ChunkParser):
    def __init__(self):
        super(NotesParser, self).__init__()
        self.plvl = None
        self.bot = False
        # Number of times worshipped a new god. (Doesn't count
        # initial gods from zealot backgrounds)
        self.conversions = 0
        self.runes_so_far = 0

    @staticmethod
    def interested(chunk):
        return chunk[0] == 'notes'

    def _parse_with_morgue(self, chunk, morgue):
        global _NOTEPARSERS
        self.morgue = morgue
        # Have to skip "Notes" title, then column headings, then hr
        note_idx_start = 3 
        # Some notes sections have a trailing line with some spaces (not just
        # a newline, which would be ommitted by next_chunk())
        trailing = chunk[-1] == ''
        note_idx_end = len(chunk) - (1 if trailing else 0)
        for noteline in chunk[note_idx_start:note_idx_end]:
            try:
                turn, place, note_text = [text.strip() for text in noteline.split('|', 2)]
            except ValueError:
                # This turns out to happen pretty often. Frequently the problem
                # is with the last line, which may be a bunch of spaces, or
                # the continuation of a multi-line death message (e.g. 
                # "succumbed to an adder's poison\n... on level 3 of the Dungeon")
                if noteline:
                    print "~Warning: unparseable note line in {}:\n{}".format(
                        morgue.f.name, noteline)
                continue
            turn = int(turn)
            note = Note(note_text, place, turn) 
            for subparser in _NOTEPARSERS:
                res = subparser(self, note)
                if res is not None:
                    for k, v in res:
                        yield k, v

        yield 'nrunes', self.runes_so_far
        yield 'religious_experiences', self.conversions
        yield 'bot', self.bot
        if morgue.name in morgue.bots and not self.bot:
            print ("WARNING: {} was in list of known bots, but seemed not to"
                +" be botting this game: {}").format(morgue.name, morgue.f.name)
    @noteparser
    def botline(self, note):
        # elliptic's qw bot (which I think is the only one really in use, or 
        # at least the most popular), leaves some telltale marks in the notes
        # section. 
        if not self.bot and re.search('\d+ \|\|\| ', note.text):
            self.bot = True
            self.morgue.bots.add(self.morgue.name)

    @noteparser
    def mutation(self, note):
        # There are some weird situations where the notes will say that the
        # player gained mutation X from source Y on turn Z, and then the
        # next note will say the player lost X from Y on Z. Bug I guess?
        # Not going to try to correct for it for now.
        m = re.match('(gained|lost) mutation:.*\[(.*)\]$', note.text)
        if m:
            source = m.group(2)
            # Trying to avoid allowing a huge number of categories in here. 
            # One source of a lot of variation is "unique x/wand of polymorph other"
            if 'wand of polymorph other' in source:
                source = 'wand of polymorph other'
            # May also want to collapse together different species intrinsics
            yield ('mutations', 
                    {'gained': m.group(1)=='gained', 'source': source, 'turn': note.turn}
                  )

    @noteparser
    def reached_temple(self, note):
        if note.text == 'found a staircase to the ecumenical temple.':
            assert note.place.startswith('d:'), note
            temple_lvl = int(note.place[2:])
            yield 'temple_depth', temple_lvl
            assert self.plvl is not None, "Found temple before reaching xl 1?"
            yield 'temple_xl', self.plvl

    @noteparser
    def got_rune(self, note):
        m = re.match('got an? (\w+) rune of zot', note.text)
        if m:
            # Use 1-based indexing
            yield 'runes',  {'rune': m.group(1), 'order': self.runes_so_far+1, 'xl': self.plvl}
            self.runes_so_far += 1

    @noteparser
    def conversion(self, note):
        # Converted?
        # TODO: this conversion info really belongs in a separate table.
        # then we can easily capture the where/what/when of each religious
        # event in a player's lifetime
        worship_prefix = 'became a worshipper of '
        if note.text.startswith(worship_prefix):
            self.conversions += 1
            if self.conversions == 1:
                fancyname = note.text[len(worship_prefix):]
                god = crawl_data.lookup_fancy_god_name(fancyname)
                yield 'first_conversion', god
                if note.place == 'temple':
                    where = 'temple'
                elif note.place.startswith('d:'):
                    lvl = int(note.place[2:])
                    if lvl > 9:
                        where = 'other'
                    else:
                        where = note.place
                else:
                    where = 'other'
                yield 'whereconverted', where

    @noteparser
    def level_up(self, note):
        m = re.match('reached xp level (\d+)', note.text)
        if m:
            self.plvl = int(m.group(1))



