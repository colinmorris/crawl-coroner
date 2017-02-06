import re

from base import ChunkParser
from .. import crawl_data
from ..coroner_exceptions import *

class SummaryParser(ChunkParser):
    topline_re = re.compile('(?P<score>\d+) (?P<name>[^ ]*) .*\(level (?P<level>\d+),')
    @classmethod
    def interested(kls, chunk):
        # probably sufficient just to return True, but whatever
        return re.match(kls.topline_re, chunk[0])

    # TODO: split me up into helper methods
    @classmethod
    def _parse_with_morgue(kls, lines, morgue):
        """Parse the section at the top, after the version line.
        Frodo the Vexing (level X)
        began as a merfolk haberdasher
        etc."""
        match = re.match(kls.topline_re, lines[0])
        assert match, "Couldn't find score/name/level in line: " + lines[0] 
        d = match.groupdict()
        # Save player name for future logging
        morgue.name = d['name']
        yield 'score', int(d['score'])
        yield 'level', int(d['level'])

        match = re.match('began as an? (.*) on', lines[1])
        assert match, lines[1]
        combo = match.group(1)
        parts = combo.split()
        if len(parts) == 2:
            sp, bg = parts
        elif parts[0] in crawl_data.CANON_SPECIES:
            sp = parts[0]
            bg = ' '.join(parts[1:])
        # Was renamed in 0.10
        elif parts[0] == 'kenku':
            sp = 'tengu'
            bg = ' '.join(parts[1:])
        elif parts[0] in crawl_data.WEIRD_SPECIES:
            raise ExperimentalComboException
        else:
            sp = ' '.join(parts[:2])
            bg = ' '.join(parts[2:])
        if sp == 'kenku':
            sp = 'tengu'
        if sp not in crawl_data.CANON_SPECIES:
            # Not a canonical species. Hopefully it's a devil we know.
            assert sp in crawl_data.WEIRD_SPECIES, "Unrecognized species: {}".format(sp)
            raise ExperimentalComboException

        if bg not in crawl_data.CANON_BGS:
            assert bg in crawl_data.WEIRD_BGS, "Unrecognized bg: {}".format(bg)
            raise ExperimentalComboException
        
        yield 'species', sp
        yield 'bg', bg

        # Seems to be some inconsistency in which lines appear where in this
        # blob. May get a line about god worshipped, if there was one, 
        # inconsistent info on timing/duration, and possibly some hard wrapping
        # We want to muddle our way through this and eventually find out whether
        # this character won or died, and where they died
        i = 2
        won = None
        wheredied = None
        howdied = None
        while i < len(lines):
            line = lines[i]
            i += 1
            if line.startswith('escaped with the orb'):
                won = True
                break
            if (line == 'safely got out of the dungeon.'
                    or line == 'got out of the dungeon alive.'
                    or line.startswith('quit the game')
                    or line == 'got out of the dungeon'
                ):
                howdied = 'quit'
                won = False
                break
            # TODO :What is 'burnt to a crisp'?
            # Man, there is a lot of variety in these messages. :(
            # TODO: Killed from afar one not strictly correct. Could rarely be god wrath
            # ('killed from afar by the fury of makhleb')
            monster_death_prefixes = ['slain by', 'mangled by', 'shot with',
                    'killed from afar', 'hit by', 'demolished by', 'annihilated by',
                    # This one mostly appears in the context of 
                    # 'Killed by X\n... invoked by Y' (smiting, pain)
                    # Can also prefix miscasts (checked earlier), and some
                    # other weird, rare stuff (killed by angry trees, killed by a
                    # spatial distortion.
                    'killed by',
                    # This one is kinda weird. Maybe the result of too much draining
                    # at a low level, exhausting all xp or something? v rare
                    'was drained of all life',
                    'drained of all life',
                    'blown up by', 'splashed by', 'splashed with', 'drowned by',
                    # How the hell?
                    'thrown by',
                    # Dying to a monster's poison is maybe not really worth
                    # distinguishing from the general case of dying to a monster
                    'succumbed to',
                    # I guess the same goes for sticky flame
                    'burnt to a crisp',
                    'incinerated by',
                    'impaled on', 'headbutted by', 'rolled over by'
            ]
            if line.startswith('killed by miscasting'):
                howdied = 'miscast'
            elif line == 'succumbed to poison (a potion of poison)':
                howdied = 'suicide'
            elif line.startswith('distortion unwield') or line.startswith('killed by distortion unwield'):
                howdied = 'suicide'
            # Above checks need to happen first, since they're subsumed by more
            # generic monster death prefixes
            elif (any(line.startswith(pre) for pre in monster_death_prefixes)
                    ):
                howdied = 'monster'
            elif 'themsel' in line:
                # This has the happy effect of setting the correct cause of death
                # for "Killed by an exploding spore\n...Set off by themselves"
                howdied = 'suicide'
            elif line.startswith('rotted away'):
                howdied = 'rot'
            elif line.startswith('engulfed by'):
                # Hacky approximation. If it originated from a monster, it'll
                # be something like "Engulfed by a death drake's foul pestilence",
                # or "an ice statue's freezing vapour", otherwise it'll just be
                # something like "engulfed by a cloud of flame"
                howdied = 'monster' if "'s" in line else 'cloud'
            elif line.startswith('starved to death'):
                howdied = 'starved'
            elif line == 'asphyxiated':
                howdied = 'asphyxiated'
            elif (line == 'drowned' or line == 'took a swim in molten lava'
                    or line == 'turned to ash by lava'):
                howdied = 'drowned'
            elif (line == 'forgot to exist' or line == 'slipped on a banana peel'
                    or line == 'forgot to breathe'):
                howdied = 'statdeath'


            r = ('\.\.\. (in|on level (?P<lvl>\d+) of) ((the|a|an) )?'
                    +'(?P<branch>.*?)( on .*)?.$')
            m = re.match(r, line)
            if m:
                wheredied = m.group('branch')
                won = False
                break

        assert won is not None, "Couldn't figure out whether they won: {}".format(lines)
        # This isn't a dealbreaker. We should just record a row with nan for howdied.
        if not (won or howdied):
            print "Warning: Couldn't determine cause of death for: {}".format(lines)
        yield 'won', won
        yield 'wheredied', wheredied and kls.normalize_wheredied(wheredied)
        yield 'howdied', howdied

        timeline = lines[-1]
        match = re.match('the game lasted (.*) \((\d+) turns?\)', timeline)
        assert match, 'Unexpected line: {}'.format(timeline)
        timestr, turns = match.groups()
        parts = timestr.strip().split()
        # '1day 11:22:33', or '1 day 11:22:33' or '11:22:33'
        assert 1 <= len(parts) <= 3, timestr
        if len(parts) == 2:
            digits = [c for c in parts[0] if c.isdigit()]
            days = int(''.join(digits))
        elif len(parts) == 3:
            days = int(parts[0])
        else:
            days = 0
        hrs, mins, secs = map(int, parts[-1].split(':'))
        total_seconds = secs + 60*mins + 60*60*hrs + 24*60*60*days
        yield 'time', total_seconds
        yield 'turns', int(turns)
    
    @staticmethod
    def normalize_wheredied(wd):
        if wd in crawl_data.CANON_WD:
            return wd
        if wd == 'tomb of the ancients':
            return 'tomb'
        if wd == "spider's nest":
            return "spider nest"
        if wd.startswith('level') and 'ziggurat' in wd:
            return 'ziggurat'
        if wd == "pandemonium (cerebov's castle)":
            return 'pandemonium'
        if wd == 'sewers':
            return 'sewer'
        if wd.startswith('ecumenical temple'):
            # Sometimes see "ecumenical temple (autumnal temple)". No idea.
            return 'ecumenical temple'
        if wd in crawl_data.WIZLABS:
            return "wizard's laboratory"
        return 'other'
