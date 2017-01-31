def xlabel_pct(ax):
    ax.set_xticklabels('{}%'.format(x*100) for x in ax.get_xticks())
def ylabel_pct(ax):
    ax.set_yticklabels('{}%'.format(y*100) for y in ax.get_yticks())
    
def plot_percent(df, horizontal=False, **kwargs):
    pfunc = df.plot.barh if horizontal else df.plot.bar
    ax = pfunc(**kwargs)
    if horizontal:
        xlabel_pct(ax)
    else:
        ylabel_pct(ax)
    return ax
