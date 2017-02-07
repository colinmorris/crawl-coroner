This repo is concerned with parsing and analyzing morgue files from [Dungeon Crawl Stone Soup](https://crawl.develz.org/) on a large-ish scale. 

I was able to download about 1.5m reasonably recent games from [http://crawl.akrasiac.org/](http://crawl.akrasiac.org/). If you're interested in playing with the data, I've uploaded a tarball of the morgues at:

    https://s3.amazonaws.com/dcss/morgues.tar.gz

(3.4GB compressed, 20-something GB uncompressed)

- `parse.py` parses a whole bunch of morgue files and flushes some salient bits of structured data to a bunch of pandas dataframes stored in hdf5.
- `coroner/crawl_data.py`: mostly enumerations of some static categories in the game (skills, species, gods, places, etc.)
- \*.ipynb: a bunch of ipython notebooks, each exploring some particular theme in DCSS
- `vis_common.py`: helper functions used across different ipython notebooks, mostly involving plotting

