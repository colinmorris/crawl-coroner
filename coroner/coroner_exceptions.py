class CoronerException(Exception):
    pass
    
class RoutineCoronerException(CoronerException):
    pass

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
