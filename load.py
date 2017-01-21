import pandas as pd

fname = 'morgue.h5'
store = pd.HDFStore(fname)

def load_frame(mini=False):
    if mini:
        return store['mini']
    return store['m']
