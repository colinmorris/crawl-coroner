
"""
Pseudocode

we have a stable of chunk parsers, ordered in roughly the order they expect
to be woken up in a typical morgue file

for each chunk in the morgue file...
    find an unwoken parser interested in this chunk
    (if none exists, continue)
    for each column/row/datum yielded by the chunkparser...
        add it to our data structures
    (chunk parser might also mutate Morgue object in exceptional circumstances,
    like to set the name attribute? feels kind of ugly though)

Maaaaybe these should even live in a separate sub-package?
"""
class ChunkParser(object):
    # DEPRECATED
    order = -1
    # TODO: Might want to define level of 'out of order tolerance' for
    # each parser?
    # shy => may yield no tuples for an interesting chunk
    shy = False
    optional = False
    @staticmethod
    def interested(chunk):
        return True

    @classmethod
    def parse(kls, chunk, morgue):
        if hasattr(kls, '_parse'):
            return kls._parse(chunk)
        elif hasattr(kls, '_parse_with_morgue'):
            return kls._parse_with_morgue(chunk, morgue)
        else:
            raise NotImplementedError()
