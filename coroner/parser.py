import re
import pandas as pd
import traceback
from collections import defaultdict

import crawl_data
from coroner_exceptions import *
from chunk_parsers import parsers


# TODO: There's probably a more elegant way to structure this. Like, define
# modular 'chunk parsers', that each have some logic for:
#   - whether they're interested in a particular chunk
#   - what to do with a chunk they're interested in
# Then this class could just be responsible for chunking the file and farming it
# out to those mini parsers.

class Morgue(object):
    # Keep track of seen bots so we can save them to a file at the end for later use
    bots = set()
    def __init__(self, f):
        self.f = f
        self.game_row = {}
        self.ancillary_rows = defaultdict(list)
        self.name = None # player name
        try:
            self.parse()
        except Exception as e:
            e.fname = self.f.name
            e.version = self.m.get('version', 'UNK')
            # Unfortunately, it seems like the original line number gets lost
            # when reraising. This seems like a hack. Is there no better way?
            e.trace = traceback.format_exc(e)
            raise e

    def setcol(self, col, value, table='game'):
        dest = self.game_row if table == 'game' else self.ancillary_rows[table]
        dest[col] = value

    def setrow(self, rowdict, table):
        assert table not in self.ancillary_rows, 'Tried to overwrite {}'.format(table)
        self.ancillary_rows[table] = rowdict


    def parse(self):
        # TODO: WIP
        c1, c2 = self.next_chunk(), self.next_chunk()
        for (parser, chunk) in zip( parsers, (c1,c2) ):
            for k, v in parser.parse(chunk, self):
                self.setcol(k, v)

        self.next_chunk()
        lines = self.next_chunk()
        godline = lines[1]
        parts = godline.split()
        try:
            gindex = parts.index('god:') + 1
        # Weird spacing issues with big stats?
        except ValueError:
            for i, part in enumerate(parts):
                if 'god:' in part:
                    gindex = i + 1
                    break
            else:
                raise Exception('Weird line: ' + godline)
        if gindex == len(parts):
            # there is no god
            god = 'none'
        # Xom formatting is a bit wonky
        elif parts[0] in ('xom', '*xom'):
            god = 'xom'
        elif gindex == len(parts) - 1: # Special case for gozag, who doesn't have piety
            god = parts[gindex]
        else:
            god = ' '.join(parts[gindex:-1])
            assert god, godline
        # Sometimes we'll get a string like '*Zin', meaning worshipping Zin but under penance
        if god[0] == '*':
            god = ' '.join(parts[gindex:])[1:]
        # Apparently some inconsistency in case for TSO
        god = god.lower()
        assert god == 'none' or god in GODS, 'Unrecognized god: {}'.format(god)
        self.setcol('god', god)

        percent = self.next_chunk()

        lines = self.next_chunk()
        statuses = lines[0]
        # TODO: handle statuses
        # TODO: introduces columns with mostly missing values. Problem? Should look into sparse data structures.
        i = 0
        while i < len(lines):
            line = lines[i]
            i += 1
            if line.startswith('}:'):
                # wrapping. This is gonna be a recurring problem.
                if line.endswith(','):
                    line += ' ' + lines[i]
                    i += 1
                match = re.match(r'}: (\d+)/15 runes: (.*)$', line)
                n, runestr = match.groups()
                self.setcol('nrunes', int(n))
                runes = [rune.strip() for rune in runestr.split(',')]
                for rune in runes:
                    assert rune, 'Got into a bad rune situation: {}'.format(lines)
                    self.setcol('rune_{}'.format(rune), True)
                break

        # You were in the dungeon, you worshipped X, you were hungry, etc.
        while 1:
            chunk = self.next_chunk()
            if chunk[0].startswith('you visited'):
                break
            # Pretty sure these usually come before 'you visited', but should be robust to different orders
            for line in chunk:
                if line in crawl_data.HUNGER_LINES:
                    self.setcol('hunger', crawl_data.HUNGER_LINES[line])

        visited = chunk
        assert visited[0].startswith('you visited'), 'Bad visit chunk. First line: {}'.format(visited[0])
        for line in visited:
            # Maybe this should have been done in next_chunk. Probably too late now.
            line = line.strip().lower()
            prefix = 'you also visited: '
            if not line.startswith(prefix):
                continue
            # Skip the last char, which is a period.
            portalstr = line[len(prefix):-1].replace(' and', ',')
            portals = portalstr.split(', ')
            for portal in portals:
                try:
                    # Sometimes get stuff like 'labyrinth (2 times)'
                    # TODO: this is probably information I should record for the
                    # purposes of some analyses, though I think it's a pretty 
                    # rare phenomenon (is it even possible to get 2 of the same 
                    # portal vault in one game in the current version?)
                    paren = portal.index('(')
                    portal = portal[:paren]
                except ValueError:
                    pass
                self.setcol('visited_'+portal.strip(), True)


        # Originally relied on fixed ordering of chunks, but it turns out there's
        # some variation between versions, so just scan for known chunk headers
        # anywhere
        header_to_method = {
                'skills:': self.parse_skills,
                'branches:': self.parse_branches,
                'notes': self.parse_notes,
        }
        sought = header_to_method.keys()
        while sought:
            try:
                chunk = self.next_chunk()
            except ChunkExhaustionException as e:
                e.message = 'Traversed whole file without finding headers: {}'.format(sought)
                raise e
            header = chunk[0]
            if header in sought:
                header_to_method[header](chunk)
                sought.remove(header)
        
        
    def parse_skills(self, chunk):
        # Parse skill levels
        # It seems like a nice idea to have some kind of series/dataframe nested
        # inside the main one for stuff like runes, skills, spells, etc. (if only
        # for the sake of tidiness and not having to do ersatz namespacing), but 
        # it seems like that's something that's not really well-supported by pandas?
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
            self.setcol('skill_'+skill_name, lvl)

    def parse_branches(self, chunk):
        blob = ' '.join(chunk[1:])
        tokens = blob.split()
        i = 0
        # Looking around for substrings like 'Temple (1/1) D:7'
        while i < len(tokens):
            w = tokens[i]
            i += 1
            if w not in crawl_data.BRANCHES:
                continue
            branch = w
            w = tokens[i]
            i += 1
            # I think this indicates the player has at least seen the entrance
            # I think (0/X) means they haven't entered it. If they've been to
            # the range of levels where it should appear, but haven't seen the
            # entrance, they get something like 'Vaults: D:13-D14'
            if w[0] == '(':
                self.setcol('saw_'+branch, True)


    def parse_notes(self, chunk):
        plvl = None
        # Number of times worshipped a new god. (Doesn't count
        # initial gods from zealot backgrounds)
        conversions = 0
        runes_so_far = 0
        for noteline in chunk:
            turn, place, note = [text.strip() for text in noteline.strip('|', 2)]
            # Bot?
            # elliptic's qw bot (which I think is the only one really in use, or 
            # at least the most popular), leaves some telltale marks in the notes
            # section. 
            if re.search('\d+ \|\|\| ', note):
                self.setcol('bot', True)
                self.bots.add(self.name)
            elif self.name in self.bots:
                print "WARNING: {} was in list of known bots, but seemed not to be botting this game: {}".format(self.f.name)

            # Reached temple?
            if noteline == 'found a staircase to the ecumenical temple.':
                assert place.startswith('D:'), noteline
                temple_lvl = int(place[2:])
                self.setcol('temple_depth', temple_lvl)
                assert plvl is not None, "Found temple before reaching xl 1?"
                self.setcol('temple_xl', plvl)

            # Leveled up?
            m = re.match('reached xp level (\d+)', note)
            if m:
                plvl = int(m.group(1))

            # Converted?
            worship_prefix = 'became a worshipper of '
            if note.startswith(worship_prefix):
                conversions += 1
                fancyname = note[len(worship_prefix):]
                god = crawl_data.lookup_fancy_god_name(fancyname)
                self.setcol('first_conversion', god)

            # Got a rune?
            m = re.match('got a (\w+) rune of zot')
            if m:
                self.setrow(
                    # Use 1-based indexing
                    {'rune': m.group(1), 'order': runes_so_far+1},
                    'runes'
                )
                runes_so_far += 1

        self.setcol('religious_experiences', conversions)

            

    def next_chunk(self):
        """Return the next "chunk" in this morgue file - i.e. the next non-blank
        line and all lines after it until the next blank line - as a list of strings 
        (which we strip and lowercase before returning)"""
        chunk = []
        while 1:
            line = self.f.readline()
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

    def next_line(self):
        """Return the next non-blank line, stripped and lowercased."""
        while 1:
            line = self.f.readline()
            if line == '':
                raise ChunkExhaustionException()
            elif line == '\n':
                continue
            return line.strip().lower()
