class CoronerException(Exception):
    pass

class ParseException(CoronerException):
    """Generic umbrella for any unexpected condition encountered during 
    parsing ("unknown unknowns" - in contrast with RoutineCoronerExceptions)."""
    pass
    
class RoutineCoronerException(CoronerException):
    """Something about this morgue file makes it unsuitable to be added to 
    the dataset. But it's a failure mode we're aware of."""
    pass

class MissingChunkException(RoutineCoronerException):
    def __init__(self, chunks):
        msg = "Couldn't find chunks: {}".format(chunks)
        super(MissingChunkException, self).__init__(msg)
        chunkstr = '_'.join(chunks)
        self.key = "missing_chunk_{}".format(chunkstr)

class CritMissingChunkException(CoronerException):
    def __init__(self, chunks):
        msg = "Couldn't find chunks: {}".format(chunks)
        super(CritMissingChunkException, self).__init__(msg)
        chunkstr = '_'.join(chunks)
        self.key = "missing_chunk_{}".format(chunkstr)

class VersionException(CoronerException):
    """Unrecognized version string"""
    pass

class OldVersionException(RoutineCoronerException):
    pass

class ChunkExhaustionException(CoronerException):
    pass

class MinigameException(RoutineCoronerException):
    """Raised if this is a sprint/zot defense game rather than crawl proper"""
    pass

class ExperimentalComboException(RoutineCoronerException):
    """Raised for games involving experimental species or backgrounds - ones that
    never made it into a release. We exclude these from the data since they represent
    a small, noisy sample, and generally make things awkward.
    """
    pass
