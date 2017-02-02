from vis_common import STORE as S, load_frame
from crawl_data import CANON_SPECIES, CANON_BGS

f = load_frame(mini=False, raw=True, include=['bot'])

# TODO: Put mini frame in here, if it's still needed.
# Or maybe mini should just be chunk0. Though there's kind of a sampling bias there?

# Stable of reusable/composable indices
# TODO: is there much point to this? They're not expensive to compute.
# Main advantage is that they can be applied to any slices (whereas
# if you import a cleaned version of the data, create an 'iwon' index
# from it, and later load some bot games and try to reuse the same 
# index, it won't work.
S['iwon'] = f['won'] == True
S['ilost'] = f['won'] == False
S['irecent'] = f['version'] > .16
S['iquit'] = f['howdied']=='quit'

# Index for a 'cleaned' version of the dataset (excluding trivial games, bots,
# and weird species/bgs that never made it into a release)
S['icleaned'] = (f['species'].isin(CANON_SPECIES) 
        & f['bg'].isin(CANON_BGS)
        & (f['bot'] == False)
        & (~ ( (f['level'] == 1) & (f['howdied'] == 'quit') ) )
)

S.put('bots', f[f['bot']==True], format='table')
