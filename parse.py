import os
import sys
import re
import pandas as pd
from distutils.version import StrictVersion
from collections import Counter
import time
import traceback

SPECIES = ('Human,High Elf,Deep Elf,Deep Dwarf,Hill Orc,Halfling,Kobold,Spriggan,Ogre,Troll,Naga,'
        + 'Centaur,Merfolk,Minotaur,Tengu,Draconian,Gargoyle,Formicid,Vine Stalker,Demigod,Demonspawn,'
        + 'Mummy,Ghoul,Vampire,Felid,Octopode,'
        + 'Black Draconian,Purple Draconian,Green Draconian,Yellow Draconian,Red Draconian,'
        + 'Mottled Draconian,White Draconian,Grey Draconian,Pale Draconian,'
        # Legacy/in development (wtf is a Grotesk?)
        + 'Mountain Dwarf,Djinni,Lava Orc,Sludge Elf,Barachian,Kenku,Grotesk'
        ).split(',')

BGS = ('Fighter,Gladiator,Monk,Hunter,Assassin,Artificer,Wanderer,Berserker,Abyssal Knight,'
        + 'Chaos Knight,Skald,Transmuter,Warper,Arcane Marksman,Enchanter,Wizard,Conjurer,'
        + 'Summoner,Necromancer,Fire Elementalist,Ice Elementalist,Air Elementalist,'
        + 'Earth Elementalist,Venom Mage,'
        # Legacy
        + 'Stalker,Priest,Healer,Paladin,Death Knight').split(',')

STRICT_BG_CHECK = 0

MAX_UNSUPPORTED_VERSION = StrictVersion('0.9')

class VersionException(Exception):
    pass

class OldVersionException(Exception):
    pass

class Morgue(object):
    def __init__(self, f):
        self.f = f
        # The core morgue data structure. Used for simple scalar columns.
        self.m = {}
        self.skills = {}
        try:
            self.parse()
        except Exception as e:
            e.fname = self.f.name
            e.version = self.m.get('version', 'UNK')
            # Unfortunately, it seems like the original line number gets lost
            # when reraising. This seems like a hack. Is there no better way?
            e.trace = traceback.format_exc(e)
            raise e

    def setcol(self, col, value):
        # I thought I needed to inject some behaviour here, but turns out I don't.
        self.m[col] = value

    def parse(self):
        l = self.next_line()
        vstring = l.split()[5]
        # Simplifying(?)
        match = re.match('\d\.\d+', vstring)
        if not match:
            raise VersionException(vstring)
        v = match.group()
        if StrictVersion(v) <= MAX_UNSUPPORTED_VERSION:
            raise OldVersionException()
        self.setcol('version', v)

        lines = self.next_chunk()
        match = re.match('(?P<score>\d+) (?P<name>[^ ]*) .*\(level (?P<level>\d+),', lines[0])
        assert match, lines[0] 
        d = match.groupdict()
        self.setcol('score', int(d['score']))
        self.setcol('level', int(d['level']))

        match = re.match('\s*Began as an? (.*) on', lines[1])
        assert match, lines[1]
        combo = match.group(1)
        parts = combo.split()
        if len(parts) == 2:
            sp, bg = parts
        elif parts[0] in SPECIES:
            sp = parts[0]
            bg = ' '.join(parts[1:])
        else:
            sp = ' '.join(parts[:2])
            bg = ' '.join(parts[2:])
        try:
            assert sp in SPECIES, 'Unrecognized species: {}'.format(sp)
            assert bg in BGS, 'Unrecognized background: {}'.format(bg)
        except AssertionError as e:
            if STRICT_BG_CHECK:
                raise e
            else:
                print e.message
        self.setcol('species', sp)
        self.setcol('bg', bg)

        outcome = lines[3]
        won = outcome.strip().lower().startswith('escaped with the orb')
        self.setcol('won', won)

        # TODO: Death place

        self.next_chunk()
        lines = self.next_chunk()
        godline = lines[1]
        parts = godline.split()
        gindex = parts.index('God:') + 1
        if gindex == len(parts):
            # there is no god
            god = None
        # Xom formatting is a bit wonky
        elif parts[0] == 'Xom':
            god = parts[0]
        elif gindex == len(parts) - 1: # Special case for gozag, who doesn't have piety
            god = parts[gindex]
        else:
            god = ' '.join(parts[gindex:-1])
            assert god, godline
        # Sometimes we'll get a string like '*Zin', meaning worshipping Zin but under penance
        if god and god[0] == '*':
            god = ' '.join(parts[gindex:])[1:]
        # Apparently some inconsistency in case for TSO
        god = god and god.lower()
        self.setcol('god', god)

        percent = self.next_chunk()

        lines = self.next_chunk()
        statuses = lines[0]
        # TODO: handle statuses
        # TODO: introduces columns with mostly missing values. Problem?
        # TODO: should probably tell pandas to replace missing values
        # of rune_foo with False, nrunes with 0, skill_foo with 0.0, etc.
        for line in lines:
            if line.startswith('}:'):
                match = re.match(r'}: (\d+)/15 runes: (.*)$', line)
                n, runestr = match.groups()
                self.setcol('nrunes', n)
                runes = [rune.strip() for rune in runestr.split(',')]
                for rune in runes:
                    self.setcol('rune_{}'.format(rune), True)
                break

        # Parse skill levels
        # It seems like a nice idea to have some kind of series/dataframe nested
        # inside the main one for stuff like runes, skills, spells, etc. (if only
        # for the sake of tidiness and not having to do ersatz namespacing), but 
        # it seems like that's something that's not really well-supported by pandas?
        while 1:
            chunk = self.next_chunk()
            if chunk[0].strip() == 'Skills:':
                break
        for skill_line in chunk[1:]:
            match = re.search('Level (\d+\.?\d?)', skill_line)
            assert match, skill_line
            lvl = float(match.group(1))
            parts = skill_line.split()
            skill_name = ' '.join(parts[3:]) # brittle
            self.setcol('skill_'+skill_name, lvl)

    def next_chunk(self):
        chunk = []
        while 1:
            line = self.f.readline()
            if line == '\n':
                # The last call read until it encountered a blank line. But
                # sometimes there's more than one consecutive blank line, which
                # we need to power through before getting to the good stuff
                if len(chunk) == 0:
                    continue
                else:
                    break
            chunk.append(line)
        return chunk

    def next_line(self):
        line = self.f.readline()
        assert line != '\n'
        skip = self.f.readline() 
        assert skip == '\n', 'Expected nothing, got {}'.format(skip)
        return line

if __name__ == '__main__':
    t0 = time.time()
    morgue_dir = sys.argv[1]
    rows = []
    cols = []
    skips = Counter()
    for parent, _, fnames in os.walk(morgue_dir):
        for fname in fnames:
            if not fname.endswith('.txt') or not fname.startswith('morgue'):
                continue
            with open(os.path.join(parent, fname)) as f:
                try:
                    morg = Morgue(f)
                except VersionException as ve:
                    skips['vstring'] += 1
                    continue
                except OldVersionException as ove:
                    skips['old'] += 1
                    continue
                except Exception as e:
                    print "Unhandled exception in file {}. Version={}".format(e.fname, e.version)
                    print "Original trace: {}".format(e.trace)
                    raise e
                rows.append(morg.m)

    frame = pd.DataFrame(rows)
    frame['nrunes'].fillna(0, inplace=1)
    for col in frame.columns:
        if col.startswith('rune_'):
            frame[col].fillna(False, inplace=1)
        elif col.startswith('skill_'):
            frame[col].fillna(0.0, inplace=1)

    print "Finished after {:.0f} seconds".format(time.time()-t0)

    DEBUG = 1
    if DEBUG:
        print "Skips: {}".format(skips)
        for col in ['god', 'bg', 'species', 'version']:
            print col
            print frame[col].unique()
            print

        print "n = {}".format(len(frame))


