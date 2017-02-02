import pandas as pd

STORE_FNAME = 'morgue.h5'
    

# This is probably expensive. But then it only really needs to be run once.
if __name__ == '__main__':
    store = pd.HDFStore(STORE_FNAME)

    # other derived columns of interest:
    # - player experience/skill

    games = store['games']

    # Original species: doing any kind of naive analysis across species tends to
    # result in weird outcomes for draconians, because the population of baby
    # draconians is very different from the population of coloured draconians
    # (who must have made it to at least level 7). This column is the same
    # as species, except that all draconian species are merged into one.
    species = games['species'].cat.categories
    drac_species = set(sp for sp in species if 'draconian' in sp)
    def get_original_species(sp):
        return 'draconian' if sp in drac_species else sp
    
    games['orig_species'] = games['species'].map(get_original_species)

    # "legit-ness". There are some 'junk' games that will tend to just pollute
    # the results of a lot of typical analyses, namely:
    # - games played by bots
    # - games quit at level 1
    # There's an argument to be made for making the latter condition more extreme 
    # and just excluding all quit games.
    # Though actually, maybe that's a bad argument. Because I think some
    # players will quit when they get into a clearly hopeless situation
    # as some kind of face-saving gesture.
    # Excluding level 1 quits was based on the empirical observation that
    # there are a shit-ton of quits at level 1 (which probably don't 
    # meaningfully reflect how the game would have gone if the player
    # had actually tried to win). Would be good to sniff around the
    # data some time to see if there are any patterns in these lvl
    # 1 quitters.
    games['legit'] = (~games['bot'] & 
            ~( (games['level'] == 1) & (games['howdied'] == 'quit'))
    )


    store.put('games', games, format='table', data_columns=['legit'])
