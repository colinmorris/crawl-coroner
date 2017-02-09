
def smoothed_winrate(df, C=10):
    """Given a games dataframe, return a similarly-indexed Series with smoothed
    winrates.
    """
    wr_prior = df['won'].mean()
    def _smooth_wincol(won_col):
        return ( (won_col.sum() + (C * wr_prior))
                / (C + len(won_col)) )
    return df.groupby('pid')['won'].agg(_smooth_wincol).loc[df['pid']]

