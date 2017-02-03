
# Just dumping some old code from parse.py here in case I want to adapt it
# later when parsing statuses and stuff
"""

        # TODO: handle statuses
        while False and i < len(lines):
            line = lines[i]
            i += 1
            if line.startswith('}:'):
                # wrapping. This is gonna be a recurring problem.
                if line.endswith(','):
                    line += ' ' + lines[i]
                    i += 1
                match = re.match(r'}: (\d+)/15 runes: (.*)$', line)
                n, runestr = match.groups()
                self.setcol('nrunes', int(n))
                runes = [rune.strip() for rune in runestr.split(',')]
                for rune in runes:
                    assert rune, 'Got into a bad rune situation: {}'.format(lines)
                    self.setcol('rune_{}'.format(rune), True)
                break
"""
