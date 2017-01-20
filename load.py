import pandas as pd

fname = 'morgue.h5'
store = pd.HDFStore(fname)
frame = store['m']
