from load import load_frame
from crawl_data import CANON_SPECIES, CANON_BGS
from matplotlib import pyplot as plt

# Use like 10% of the data. Useful for development/prototyping, cause the full dataset is getting biiiig.
MINI = 1

fr = load_frame(mini=MINI)
raw = fr
# TODO: Add some preprocessing here to filter out trivial games and bots
f = fr[ fr['species'].isin(CANON_SPECIES) 
        & fr['bg'].isin(CANON_BGS)
        & (fr['bot'] == False)
        # There's an argument to be made for making this more extreme and just excluding all quit games.
        & (~ ( (fr['level'] == 1) & (fr['howdied'] == 'quit') ) )
    ]

# Stable of reusable/composable indices
iwon = f['won'] == True
ilost = f['won'] == False
irecent = f['version'] > .16
iquit = f['howdied']=='quit'

def iall(*indices):
        return reduce(lambda x,y: x&y, indices)
        
def plot_winrate(df, by_col, title=None):
    if title is None:
        title = 'Win rate by ' + by_col
    (df.groupby(by_col)['won'].mean().dropna() * 100).sort_values().plot.barh(title=title)
    
def plot_dict(d, title='', size=(9,7), sort=True, horizontal=False):
    """Helper for plotting a bar chart for a dict with category keys"""
    fig, ax = plt.subplots(figsize=size)
    ax.set_title(title)
    if sort:
        items = sorted(d.items(), key=lambda (k,v): v, reverse=True)
    else:
        items = d.items()
    keys, values = zip(*items)
    barfn = plt.barh if horizontal else plt.bar
    barfn(range(len(d)), values, align='center')
    ticks = plt.yticks if horizontal else plt.xticks
    ticks(range(len(d)), keys)
    return fig, ax
