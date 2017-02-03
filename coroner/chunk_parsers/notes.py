import re

from base import ChunkParser
from ..coroner_exceptions import *
from .. import crawl_data


class NotesParser(ChunkParser):
    order = 7
    @staticmethod
    def interested(chunk):
        return chunk[0] == 'notes'

    @staticmethod
    def _parse_with_morgue(chunk, morgue):
        plvl = None
        bot = False
        # Number of times worshipped a new god. (Doesn't count
        # initial gods from zealot backgrounds)
        conversions = 0
        runes_so_far = 0
        # Have to skip "Notes" title, then column headings, then hr
        note_idx_start = 3 
        # Some notes sections have a trailing line with some spaces (not just
        # a newline, which would be ommitted by next_chunk())
        trailing = chunk[-1] == ''
        note_idx_end = len(chunk) - (1 if trailing else 0)
        for noteline in chunk[note_idx_start:note_idx_end]:
            try:
                turn, place, note = [text.strip() for text in noteline.split('|', 2)]
            except ValueError:
                if noteline:
                    print "~Warning: unparseable note line in {}:\n{}".format(
                        morgue.f.name, noteline)
                #raise Exception("Unparseable note line: {!r}".format(noteline))
            # Bot?
            # elliptic's qw bot (which I think is the only one really in use, or 
            # at least the most popular), leaves some telltale marks in the notes
            # section. 
            if not bot and re.search('\d+ \|\|\| ', note):
                bot = True
                morgue.bots.add(morgue.name)

            # Reached temple?
            if noteline == 'found a staircase to the ecumenical temple.':
                assert place.startswith('D:'), noteline
                temple_lvl = int(place[2:])
                yield 'temple_depth', temple_lvl
                assert plvl is not None, "Found temple before reaching xl 1?"
                yield 'temple_xl', plvl

            # Leveled up?
            m = re.match('reached xp level (\d+)', note)
            if m:
                plvl = int(m.group(1))

            # Converted?
            # TODO: this conversion info really belongs in a separate table.
            # then we can easily capture the where/what/when of each religious
            # event in a player's lifetime
            worship_prefix = 'became a worshipper of '
            if note.startswith(worship_prefix):
                conversions += 1
                if conversions > 1:
                    continue
                fancyname = note[len(worship_prefix):]
                god = crawl_data.lookup_fancy_god_name(fancyname)
                yield 'first_conversion', god
                if place == 'temple':
                    where = 'temple'
                elif place.startswith('d:'):
                    lvl = int(place[2:])
                    if lvl > 9:
                        where = 'other'
                    else:
                        where = lvl
                else:
                    where = 'other'
                yield 'whereconverted', where

            # Got a rune?
            m = re.match('got a (\w+) rune of zot', note)
            if m:
                morgue.addrow(
                    # Use 1-based indexing
                    {'rune': m.group(1), 'order': runes_so_far+1},
                    'runes'
                )
                runes_so_far += 1

        yield 'nrunes', runes_so_far
        yield 'religious_experiences', conversions
        yield 'bot', bot
        if morgue.name in morgue.bots and not bot:
            print ("WARNING: {} was in list of known bots, but seemed not to"
                +" be botting this game: {}").format(morgue.name, morgue.f.name)
