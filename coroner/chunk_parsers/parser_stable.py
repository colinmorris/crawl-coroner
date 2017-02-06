from ..coroner_exceptions import *

# TODO: would be kind of nice to know about situations where (optional) parser X *would* have 
# activated out of turn. Cause that should probably be regarded as an error (unlike the 
# situation where the parser just never gets activated). Maybe expensive to check for this
# in 'production', but could at least write a test for it.
class ChunkParserStable(object):
    """A stable of chunk parsers.
    Feed this thing a series of chunks, and it will take care of bookkeeping
    and coordination among different chunk parsers, e.g.:
    - keeping track of which parsers are done
    - choosing which parsers to try on a given chunk, making sure that our 
      constraints on ordering are obeyed
    - raising an exception if a non-shy parser fails to produce any output for
      an interesting chunk, or if we run out of chunks when there are still
      unsatisfied non-optional parsers
    """

    def __init__(self, parser_group_klasses):
        self.parser_groups = []
        for parser_klasses in parser_group_klasses:
            self.parser_groups.append([kls() for kls in parser_klasses])
        self.current_group_index = 0
        self.done = False
        # Unsatisfied, optional parsers carried over from the previous group.
        # Basically, if the only remaining parsers in a group are optional, it
        # presents a bit of a dilemma. If we keep trying those parsers every time
        # we get a chunk, we might go through all the chunks without them activating.
        # Meanwhile, the chunks we passed over might have activated one of the parsers
        # in the next group. So, if all remaining parsers in a group are optional, we
        # carry them over. Carried over parsers are checked first. If a non-carried-
        # over parser is activated, we immediately clear out any remaining carried 
        # over parsers (because of the requirement of strict ordering between groups.)
        self.carried_over = []

    def parse_chunk(self, chunk, morgue):
        # Precondition: self.parser_groups[i] has a non-done, non-optional parser
        assert not self.done
        parserses = (self.carried_over, self.parser_groups[self.current_group_index])
        labels = ('carryover', 'main')
        for parsers, label in zip(parserses, labels):
            for parser in parsers:
                if not parser.done and parser.interested(chunk):
                    did_something = False
                    for thing in parser.parse(chunk, morgue):
                        yield thing
                        did_something = True
                    # Success: the chunk was consumed, the parser is done
                    if did_something or parser.shy:
                        parser.done = True
                        if label == 'main':
                            self.carried_over = []
                        break
                    else:
                        errmsg = ('Parser {} indicated interest in chunk, but '
                                + 'produced no output, and was not marked as shy')\
                                        .format(parser.__class__.__name__)
                        raise ParseException(errmsg)

        # We want a postcondition to match our precondition: the current group
        # must have at least one non-done, non-optional parser. If that's not
        # currently the case, we need to advance to the next group.

        # See if we need to step forward to the next group of parsers
        if all(parser.done for parser in self.parser_groups[self.current_group_index]):
            self.current_group_index += 1
            if self.current_group_index == len(self.parser_groups):
                self.done = True

        elif (all(parser.done or parser.optional for parser in 
                    self.parser_groups[self.current_group_index])
              and self.current_group_index != len(self.parser_groups)-1
        ):
            self.carried_over = [p for p in self.parser_groups[self.current_group_index]]
            self.current_group_index += 1


    def check_satisfaction(self):
        """Have all non-optional chunk parsers been satisfied? If not, raise
        an exception."""
        unsat = set()
        # Starting from the last group, find any unsatisfied non-optional parsers.
        for group_idx in range(len(self.parser_groups))[::-1]:
            n0 = len(unsat)
            for parser in self.parser_groups[group_idx]:
                if not parser.done and not parser.optional:
                    unsat.add(parser.__class__.__name__)
            n1 = len(unsat)
            if n0 == n1:
                break

        if not unsat:
            return
        often_missing = {'BranchParser', 'NotesParser'}
        if unsat.issubset(often_missing):
            kls = MissingChunkException
        else:
            kls = CritMissingChunkException
        raise kls(unsat)
