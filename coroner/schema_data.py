from crawl_data import *

# For the sake of reducing the memory cost of loading data frames, we do some 
# vertical partitioning of the main 'game' table. Columns that go together in
# one of these side tables generally have some shared semantics, and a shared
# prefix.
# (Why is this necessary? See this stackoverflow question:
# http://stackoverflow.com/questions/25902114/pandas-retrieving-hdf5-columns-and-memory-usage
# Basically, when you tell hdfstore to load table X with only columns
# A,B,C, it first reads the *whole* thing in to memory, then cuts out
# the extra columns as a postprocessing step. Which almost negates the
# purpose of just loading a subset of columns at once.
PREFIX_TO_SIDE_TABLE = {
    'skill_':   'skills',
    'visited_': 'portal_vaults',
    'saw_':     'branches',
}

# XXX
DATA_COLUMNS = {'legit'}

# We use a dedicated category value for atheists to simplify analysis (and to
# make it clear that this represents "no god" not "unknown/missing god")
_god_cats = GODS.union({'none'})
# Specifying the full set of possible categories here turns out to be 
# pretty important because pandas pitches a fit if you try to append
# dataframes whose columns have different category values.
COLUMN_TO_CATEGORIES = {
    'games': {
        'bg':           CANON_BGS,
        'species':      CANON_SPECIES,
        'god':          _god_cats,
        'first_conversion': _god_cats,
        'wheredied':    CANON_WD,
        'hunger':       HUNGER_LINES.values(),
        'howdied':      CANON_HOWDIED,
    },
    'runes': {
        'rune':         RUNES,
    },
    'skill_progression': {
        'skill':        CURRENT_SKILLS, 
    },
}

COLUMN_TO_ORDERED_CATEGORIES = {
    'games': {
        'whereconverted':   ['d:1', 'd:2', 'd:3', 'd:4', 'd:5', 'd:6', 'd:7', 'd:8', 'd:9', 
            'temple', 'other']
    },
    'runes': {
        'order': range(1, 16)
    },
}

FILL_COLUMNS = {
    'games': {
        'nrunes': 0,
        'gold_spent': 0,
        'gold_collected': 0,
        'orb': False,
    },
}
