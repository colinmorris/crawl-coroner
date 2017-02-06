import os
import unittest
from nose2.tools import params
import nose2

from coroner import MorgueCollector, Morgue

testmorgue_dir = 'test_morgues'

# Another angle to attack this would be to define some generic invariants that
# should be true for any morgue file. e.g.
# - first_conversion and whereconverted should be null/non-null together
# - gold_spent <= gold_collected
# - won or wheredied
# - hp < maxhp
# - also lots of constraints on domain. Many are enforced later when converting
#   to dataframe (e.g. level in [1, 27], species in crawl_data.CANON_SPECIES, 
#   etc.). Could check those here.
# We could check these for as many morgue files as we desire without having to
# do any manual curation of expected values. Weaker, but more coverage.
morgue_to_expected = {
        'scone_FE.txt': dict(
            version=0.19,
            level=16,
            god='vehumet',
            howdied='monster',
            hp=-15, maxhp=104,
            turns=35422,
            wheredied='snake pit',
            hunger='not hungry',
            visited_labyrinth=True,
            # TODO: I can't actually specify a few keys with kwargs syntax
            # (like 'visited_ice cave'). Should probably make sure all 
            # column names are legal python identifiers.
            # ice cave
            gold_collected=3079, gold_spent=1942,
            skill_fighting=3.4, skill_armour=2.9, skill_dodging=3.4, skill_stealth=4.4,
                skill_spellcasting=16.0, skill_conjurations=16.4, # fire=13.5
            saw_temple=True, saw_lair=True, saw_shoals=True, saw_snake=True, 
                saw_slime=True, saw_orc=True, saw_elf=True, 
            temple_depth=6, temple_xl=8,
            first_conversion='vehumet', whereconverted='temple',
            bg='fire elementalist',
            won=False,
            religious_experiences=1,
            bot=False,
            score=104596,
            species='human',
            nrunes=0,
        ),
}

class TestMorgueParsing(unittest.TestCase):

    @params(*morgue_to_expected.items())
    def test_morguefile(self, fname, expected):
        with open(os.path.join(testmorgue_dir, fname)) as f:
            morg = Morgue(f)
            row = morg.game_row
            for (k, expected_val) in expected.iteritems():
                self.assertIn(k, row)
                self.assertEqual(row[k], expected_val)

            actual_keys = set(row.keys())
            expected_keys = set(expected.keys())
            untested_keys = actual_keys - expected_keys
            print "Warning: the following keys had no expected value set in {}: {!r}".format(
                    fname, untested_keys)



if __name__ == '__main__':
    nose2.main()
