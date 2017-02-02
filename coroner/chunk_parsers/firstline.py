import re
from distutils.version import StrictVersion

from base import ChunkParser
from ..coroner_exceptions import *

MAX_UNSUPPORTED_VERSION = StrictVersion('0.9')

class FirstLineParser(ChunkParser):
    order = 0
    @staticmethod
    def interested(chunk):
        # This is sort of a hack. Obviously we're not interested in all chunks,
        # but we know we'll be given the first one, because we have the highest
        # precedence, and after that we'll lie dormant.
        return True

    @staticmethod
    def _parse(chunk):
        assert len(chunk) == 1, chunk
        l = chunk[0]
        if not l.startswith('dungeon crawl stone soup version '):
            # Won't match in case of sprint, zot defense, etc.
            raise MinigameException()
        vstring = l.split()[5]
        # Simplifying(?)
        match = re.match('\d\.\d+', vstring)
        if not match:
            raise VersionException(vstring)
        v = match.group()
        if StrictVersion(v) <= MAX_UNSUPPORTED_VERSION:
            raise OldVersionException()
        yield 'version', float(v)
