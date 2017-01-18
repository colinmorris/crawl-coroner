import os
import sys
import re
import pandas as pd
from distutils.version import StrictVersion
from collections import Counter
import time
import traceback

SPECIES = [sp.lower() for sp in ('Human,High Elf,Deep Elf,Deep Dwarf,Hill Orc,Halfling,Kobold,Spriggan,Ogre,Troll,Naga,'
        + 'Centaur,Merfolk,Minotaur,Tengu,Draconian,Gargoyle,Formicid,Vine Stalker,Demigod,Demonspawn,'
        + 'Mummy,Ghoul,Vampire,Felid,Octopode,'
        + 'Black Draconian,Purple Draconian,Green Draconian,Yellow Draconian,Red Draconian,'
        + 'Mottled Draconian,White Draconian,Grey Draconian,Pale Draconian,'
        # Legacy/in development (wtf is a Grotesk?)
        + 'Mountain Dwarf,Djinni,Lava Orc,Sludge Elf,Barachian,Kenku,Grotesk'
        ).split(',')]

BGS = [bg.lower() for bg in ('Fighter,Gladiator,Monk,Hunter,Assassin,Artificer,Wanderer,Berserker,Abyssal Knight,'
        + 'Chaos Knight,Skald,Transmuter,Warper,Arcane Marksman,Enchanter,Wizard,Conjurer,'
        + 'Summoner,Necromancer,Fire Elementalist,Ice Elementalist,Air Elementalist,'
        + 'Earth Elementalist,Venom Mage,'
        # Legacy
        + 'Stalker,Priest,Healer,Paladin,Death Knight').split(',')]

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

        match = re.match('began as an? (.*) on', lines[1])
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

        # Seems to be some inconsistency in which lines appear where in this
        # blob. May get a line about god worshipped, if there was one, 
        # inconsistent info on timing/duration, and possibly some hard wrapping
        # We want to muddle our way through this and eventually find out whether
        # this character won or died, and where they died
        i = 2
        won = None
        wheredied = None
        while i < len(lines):
            line = lines[i]
            i += 1
            if line.startswith('escaped with the orb'):
                won = True
                break
            if (line == 'safely got out of the dungeon.'
                    or line == 'got out of the dungeon alive.'
                    or line.startswith('quit the game')
                ):
                won = False
                break
            r = ('\.\.\. (in|on level (?P<lvl>\d+) of) ((the|a|an) )?'
                    +'(?P<branch>.*?)( on .*)?.$')
            m = re.match(r, line)
            m1 = re.match('\.\.\. on level (\d+) of (?:(?:the|a) )?(.*).$', line)
            m2 = re.match('\.\.\. in (?:a|an|the) (.*) on ', line)
            m3 = re.match('\.\.\. in (?:(?:a|an|the) )?(.*)\.$', line)
            if m:
                wheredied = m.group('branch')
                won = False
                break

        assert won is not None, "Couldn't figure out whether they won: {}".format(lines)
        self.setcol('won', won)
        self.setcol('wheredied', wheredied)

        self.next_chunk()
        lines = self.next_chunk()
        godline = lines[1]
        parts = godline.split()
        gindex = parts.index('god:') + 1
        if gindex == len(parts):
            # there is no god
            god = None
        # Xom formatting is a bit wonky
        elif parts[0] == 'xom':
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
                    assert rune
                    self.setcol('rune_{}'.format(rune), True)
                break

        # You were in the dungeon, you worshipped X, you were hungry, etc.
        youwere = self.next_chunk()

        visited = self.next_chunk()
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
                self.setcol('visited_'+portal, True)


        # Parse skill levels
        # It seems like a nice idea to have some kind of series/dataframe nested
        # inside the main one for stuff like runes, skills, spells, etc. (if only
        # for the sake of tidiness and not having to do ersatz namespacing), but 
        # it seems like that's something that's not really well-supported by pandas?
        while 1:
            chunk = self.next_chunk()
            if chunk[0] == 'skills:':
                break
        for skill_line in chunk[1:]:
            match = re.search('level (\d+\.?\d?)', skill_line)
            assert match, skill_line
            lvl = float(match.group(1))
            skill_start = 2
            parts = skill_line.split()
            while not parts[skill_start].isalpha():
                skill_start += 1
            skill_name = ' '.join(parts[skill_start:])
            assert skill_name
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
            chunk.append(line.strip().lower())
        return chunk

    def next_line(self):
        line = self.f.readline()
        assert line != '\n'
        skip = self.f.readline() 
        assert skip == '\n', 'Expected nothing, got {}'.format(skip)
        return line.strip().lower()

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
    f = frame
    frame['nrunes'].fillna(0, inplace=1)
    for col in frame.columns:
        if col.startswith('rune_'):
            frame[col].fillna(False, inplace=1)
        elif col.startswith('skill_'):
            frame[col].fillna(0.0, inplace=1)
        elif col.startswith('visited_'):
            frame[col].fillna(False, inplace=1)
        elif col in ['bg', 'god', 'species', 'wheredied']:
            frame[col] = frame[col].astype('category')

    print "Finished after {:.0f} seconds".format(time.time()-t0)

    DEBUG = 1
    if DEBUG:
        print "Skips: {}".format(skips)
        for col in ['god', 'bg', 'species', 'version', 'wheredied']:
            print col
            print frame[col].unique()
            print

        print "n = {}".format(len(frame))

    def save(df, fname='morgue.h5'):
        with pd.HDFStore(fname) as store:
            # For some reason the format=table thing is necessary if using 
            # categorical vars. I don't really understand this.
            store.put('m', df, format='table')

    SAVE = 1
    if SAVE:
        save(frame)

