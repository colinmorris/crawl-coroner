
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
