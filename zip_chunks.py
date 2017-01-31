"""In parse.py, we write to the datastore in chunks to avoid memory issues
arising from keeping the (inefficient) dict representations of all rows
in memory at once. This script sews those chunks back together into one
dataframe, and deletes the chunks.

# TODO: unfortunately, remove()ing the chunks doesn't actually reclaim
any of the disk space they use up. Need to fiddle with ptrepack for
that sometime: http://stackoverflow.com/a/11214815/262271
"""
import pandas as pd

fname = 'morgue.h5'
store = pd.HDFStore(fname)

chunk = store['chunk0']
offset = len(chunk)
store.put('m', chunk, format='table')
chunk_index = 1
while 1:
    k = 'chunk{}'.format(chunk_index)
    if '/'+k not in store.keys():
        break
    chunk = store[k]
    # Reindex to avoid duplicates
    chunk.index = pd.Series(chunk.index) + offset
    offset += len(chunk)
    store.append('m', chunk)
    chunk_index += 1

print "Sewed together {} chunks.".format(chunk_index)

# Remove standalone chunks
# XXX: No point doing this as long as it doesn't free any space.
if 0:
    for i in range(chunk_index):
        store.remove('chunk{}'.format(i))
