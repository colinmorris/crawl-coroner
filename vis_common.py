from matplotlib import pyplot as plt
import pandas as pd

# TODO: Some kind of shared config file with parse.py etc.
STORE_FNAME = 'morgue.h5'

_STORE = None


def load_games(legit=True, extra_tables=[], n=None):
    global _STORE
    where = 'legit==True' if legit else None
    if _STORE is None:
        _STORE = pd.HDFStore(STORE_FNAME)
    if not extra_tables:
        return _STORE.select('games', stop=n, where=where)

    # Concession to my absent-mindedness
    if isinstance(extra_tables, basestring):
        extra_tables = [extra_tables]
    tables = ['games'] + extra_tables
    return _STORE.select_as_multiple(tables, where=where)


# TODO: Move these. If they're even still useful/used.
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
