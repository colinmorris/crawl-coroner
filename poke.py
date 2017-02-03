import pandas as pd

store = pd.HDFStore('morgue.h5')

f = store.select('games', stop=20)
