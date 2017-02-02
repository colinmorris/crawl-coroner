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
