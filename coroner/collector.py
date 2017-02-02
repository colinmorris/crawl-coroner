import pandas as pd
from collections import defaultdict

import crawl_data
import schema_data as schema

class MorgueCollector(object):

    def __init__(self):
        # Next available 'game id' (index of game df)
        self.gid = 0
        # Main table/dataframe, with columns describing individual games
        self.game_rows = []
        # Ancilliary tables
        self.tables_to_rows = defaultdict(list)
        self._lastflushed_id = -1
        # Autoincrementing ids per player
        self.player_lookup = defaultdict(lambda: len(self.player_lookup))
        
    def add_morgue(self, morg):
        morg.game_row['pid'] = self.player_lookup[morg.name]
        self.game_rows.append(morg.game_row)
        for table, rows in morg.ancillary_rows.items():
            for row in rows:
                row['gid'] = self.gid
                self.tables_to_rows[table].append(row)
        self.gid += 1

    def flush(self, store, final=False, flush_ancillary=False):
        """
        for each table and list of rows...
            - make an appropriate dataframe from those rows 
                (doing index offsets if necessary)
                - XXX: what does this look like for non-core tables?
            - append to the appropriate key in the store
        """
        df = self.gameframe()
        cols = df.columns
        table_to_cols = {'games': None} # Games gets all the leftovers
        for (prefix, table) in schema.PREFIX_TO_SIDE_TABLE.iteritems():
            table_to_cols[table] = [col for col in cols if col.startswith(prefix)]
        # TODO: Update df loading code.
        # TODO: May want to actually specify some data columns later so we can
        # use hdf to apply some simple where conditions when loading a frame
        # (e.g. filtering by bot is a useful one, or if we add a derived column
        # for 'legitness')
        store.append_to_multiple(table_to_cols, df, 'games', data_columns=[])
        self.game_rows = []
    
        # Players. (Might just be better off pickling a dict or something?)
        if final:
            names, pids = zip(*self.player_lookup.items())
            store['players'] = pd.Series(names, index=pids)
        if final or flush_ancillary:
            for table in self.tables_to_rows:
                df = self.ancillary_frame(table)
                store.append(table, df)

    def ancillary_frame(self, table):
        rows = self.tables_to_rows[table]
        df = pd.DataFrame(rows)
        # TODO: less ad-hoc structure for defining per-table cleaning rules
        if table == 'runes':
            df['order'] = df['order'].astype('category', categories=range(1,16),
                    ordered=True)
            df['rune'] = df['rune'].astype('category', 
                    categories=crawl_data.RUNES)
        else:
            print "~~WARNING: No data cleaning rules defined for "\
                    + "ancillary table {}".format(table)
        return df


    def gameframe(self):
        frame = pd.DataFrame(self.game_rows, 
                index=range(self._lastflushed_id+1, len(self.game_rows))
        )
        frame['nrunes'].fillna(0, inplace=1)
        for col in frame.columns:
            boolean_prefixes = ['rune_', 'visited_', 'saw_']
            if any(col.startswith(pre) for pre in boolean_prefixes):
                frame[col].fillna(False, inplace=1)
            elif col.startswith('skill_'):
                frame[col].fillna(0.0, inplace=1)

        for col, cats in crawl_data.COLUMN_TO_CATEGORIES.iteritems():
            frame[col] = frame[col].astype('category', categories=cats)

        versions = [0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20]
        frame['version'] = frame['version'].astype("category", categories=versions,
                ordered=True)
        lvls = range(1, 28)
        frame['level'] = frame['level'].astype("category", categories=lvls, ordered=True)

        non_null_cols = ['bg', 'god', 'level', 'nrunes', 'species', 'time', 'turns',
                'version', 'won',]
        for col in non_null_cols:
            if frame[col].count() != len(frame):
                print 'Got unexpected null values in column {}'.format(col)

        # Object columns are bad news in terms of memory usage.
        for col in frame.columns:
            if frame[col].dtype.name == 'object':
                print "~~~ WARNING ~~~: Column {} has object type. Are you sure " \
                        "you wouldn't rather use a category?".format(col)

        return frame

