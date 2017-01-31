import math

def _percentify(tick):
    # I know this is an abomination and there's probably an elegant way to
    # do it with proper use of str.format.
    tick *= 100
    dp = 1 # decimal points
    epsilon = 10**-3
    if tick == 0:
        return '0%'
    elif abs(tick % 1 - .5) < epsilon:
        dp = 1
    elif 0 < tick < 1:
        dp = int(abs(math.log(tick, 10)-1))
    elif tick % 1 < epsilon or (1 - tick % 1 < epsilon):
        dp = 0
    return ('{:.'+str(dp)+'f}%').format(tick)

def xlabel_pct(ax):
    ax.set_xticklabels(map(_percentify, ax.get_xticks()))
def ylabel_pct(ax):
    ax.set_yticklabels(map(_percentify, ax.get_yticks()))
    
def plot_percent(df, horizontal=False, **kwargs):
    pfunc = df.plot.barh if horizontal else df.plot.bar
    ax = pfunc(**kwargs)
    if horizontal:
        xlabel_pct(ax)
    else:
        ylabel_pct(ax)
    return ax
