import os
import sys
import pandas as pd
from collections import Counter
import time
import traceback

from coroner.coroner_exceptions import RoutineCoronerException
from coroner import MorgueCollector, Morgue

ROW_LIMIT = 0

# Running this over gbs of logs takes a while. It kind of sucks to lose all progress
# after 20 minutes because of a trivial error. If this is true, just print unhandled
# exception traces and continue
SOFT_ERRORS = 1

SAVE = 1

COPY_BADMORGUES = 0

# XXX: Sigh. The periodic flushing thing mostly works fine, except you can get 
# in an unlucky situation where your flushing period ~almost~ divides your 
# number of morgues, such that your final flush() is only flushing a tiny 
# number of games. If there's a column missing (e.g. visited_wizlab) from all 
# those rows, then trying to append will throw an error. 
# For now, let's just do it all in one big wack. Should be not too bad as 
# long as I'm running this on a reasonably beefy ec2 instance.
FLUSH_EVERY = 0
FLUSH_ANCILLARY = 0

MORGUE_FNAME = 'morgue.h5'

if __name__ == '__main__':
    t0 = time.time()
    morgue_dir = sys.argv[1]
    skips = Counter()
    niters = 0
    done = False
    if SAVE:
        fname = MORGUE_FNAME
        assert not os.path.exists(fname), "{} already exists".format(fname)
        store = pd.HDFStore(fname)

    collector = MorgueCollector() 
    for parent, _, fnames in os.walk(morgue_dir):
        for fname in fnames:
            if not fname.endswith('.txt') or not fname.startswith('morgue'):
                continue
            with open(os.path.join(parent, fname)) as f:
                try:
                    morg = Morgue(f)
                except RoutineCoronerException as e:
                    key = getattr(e, 'key', e.__class__.__name__)
                    skips[key] += 1
                except Exception as e:
                    print "Unhandled {} in file {}. Version={}".format(
                            e.__class__.__name__, getattr(e, 'fname', 'UNKNOWN_FNAME'), 
                            getattr(e, 'version', 'UNKNOWN_VERSION'),
                    )
                    if e.message:
                        print e.message
                    # May want to turn this off. It can be a little verbose. Or, y'know,
                    # just fix the code so it throws fewer unexpected exceptions.
                    if hasattr(e, 'trace'):
                        print "Original trace: {}".format(e.trace)
                    if not SOFT_ERRORS:
                        if hasattr(e, 'fname'):
                            # This really helps debugging, since it means I don't
                            # have to transcribe long strings of random digits from
                            # morgue filenames.
                            dst = 'badmorgue.txt'
                            print "Copying offending file to {}".format(dst)
                            os.system('cp {} {}'.format(e.fname, dst))
                        raise e

                    if COPY_BADMORGUES:
                        dst = 'badmorgues/{}.txt'.format(niters)
                        with open(dst, 'w') as f:
                            if e.message:
                                f.write(e.message + '\n')
                            f.write(e.trace+'\n')
                        os.system('cat {} >> {}'.format(e.fname, dst))


                    key = getattr(e, 'key', e.__class__.__name__)
                    skips[key] += 1
                else:
                    collector.add_morgue(morg)
                    niters += 1
            
                if niters and (niters % 1000) == 0:
                    print 'i={} '.format(collector.gid),

                if (ROW_LIMIT and niters >= ROW_LIMIT):
                    done = True
                    break

                if FLUSH_EVERY and niters and (niters % FLUSH_EVERY) == 0 and SAVE:
                    print "Flushing {} rows to hdfstore".format(FLUSH_EVERY)
                    collector.flush(store, flush_ancillary=FLUSH_ANCILLARY)

        if done:
            break

    # Lots of spam probably came before this
    print
    print ("*"*60+'\n')*2,
    print "Finished after {:.0f} seconds".format(time.time()-t0)
    if SAVE:
        collector.flush(store, final=True)
    else:
        # If we're not saving, we're probably running this interactively to
        # poke at the generated dataframe
        df = collector.gameframe()

    print "Skips: {}".format(skips)

    with open('known_bots.txt', 'w') as f:
        # TODO: should probably go on collector, not Morgue 
        # Also this kind of thing won't be necessary once you store a mapping
        # from game id to morgue filename. Actually, it's not even necessary now,
        # # cause you're storing pid
        f.write('\n'.join(list(Morgue.bots)) + '\n')

