This repo is concerned with parsing and analyzing morgue files from [Dungeon Crawl Stone Soup](https://crawl.develz.org/) on a large-ish scale. 

I was able to download about 1.5m reasonably recent games from [http://crawl.akrasiac.org/](http://crawl.akrasiac.org/) - if you're also interested in playing with the data, contact me and I'll see if I can share a tarball with you, so you don't need to abuse their servers like I did.

- `parse.py` parses a whole bunch of morgue files and flushes some salient bits of structured data to a bunch of pandas dataframes stored in hdf5.
- `crawl_data.py`: mostly enumerations of some static categories in the game (skills, species, gods, places, etc.)
- `zip_chunks.py` is run afterwards to combine the shards produced in the previous step into one data frame
- `store_indices.py` is run last to calculate a few useful views and indices and cache them in the store
- \*.ipynb: a bunch of ipython notebooks, each exploring some particular theme in DCSS
- vis_common.py: helper functions used across different ipython notebooks, mostly involving plotting

