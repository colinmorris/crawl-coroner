
class ChunkParser(object):
    # shy => may yield no tuples for an interesting chunk
    shy = False
    optional = False
    def __init__(self):
        self.done = False

    @staticmethod
    def interested(chunk):
        return True

    def parse(self, chunk, morgue):
        if hasattr(self, '_parse'):
            return self._parse(chunk)
        elif hasattr(self, '_parse_with_morgue'):
            return self._parse_with_morgue(chunk, morgue)
        else:
            raise NotImplementedError()

