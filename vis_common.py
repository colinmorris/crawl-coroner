from load import load_frame
from matplotlib import pyplot as plt
import pandas as pd
import gc

# Use like 10% of the data. Useful for development/prototyping, cause the full dataset is getting biiiig.
MINI = 0

MORGUE_FNAME = 'morgue.h5'
STORE = pd.HDFStore(MORGUE_FNAME)

# Columns with these prefixes won't be loaded unless explicitly asked for.
# (Fitting the whole table into memory is becoming increasingly awkward, and
# these columns - especially skills_ - account for a good majority of memory
# usage.)
OPTIONAL_COLUMN_PREFIXES = {'rune_', 'saw_', 'skill_', 'visited_'}
COLUMNS = STORE['mini'].columns
DEFAULT_COLUMNS = [col for col in COLUMNS 
                    if not any(col.startswith(pre) for pre in OPTIONAL_COLUMN_PREFIXES)
                  ]

def load_frame(mini=MINI, raw=False, include=[]):
    """Load a data frame of morgue data.
        mini: if True, just load a miniature version, consisting of around 10% of all rows
        raw: if False, filter out bot games, trivial games, and games with non-canonical species/bgs
        include: a list of columns or column prefixes to include in addition to DEFAULT_COLUMNS
    """
    framekey = 'mini' if mini else 'm'
    cols = DEFAULT_COLUMNS
    for incl in include:
        if incl in COLUMNS:
            cols.append(incl)
        elif incl in OPTIONAL_COLUMN_PREFIXES:
            cols += [col for col in COLUMNS if col.startswith(incl)]
        else:
            raise ValueError("Unrecognized column spec: {}".format(incl))
    fr = STORE.select(framekey, 'columns=cols')
    if not raw:
        fr = fr[STORE['icleaned']]
    # It's ridiculous that I have to do this :/
    gc.collect()
    return fr

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
