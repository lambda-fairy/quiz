from collections import defaultdict, namedtuple
import re


FINAL_STATES_RE = re.compile(r'\{(\d+(,\d+)*)?\}')
PATTERN_RE = re.compile(r'\((?P<state>\d+),(?P<input>\w+),(?P<stack>\w+)\)')
OUTPUT_RE = re.compile(r'\((?P<state>\d+),(?P<stack>\w+)\)')

TOKEN_RE = re.compile(r'''
    (?: (?P<final_states> \{.*?\} )
      | (?P<pattern> \(.*?\) )
        ->
        (?: (?P<output> \(.*?\) )
          | \{ (?P<outputs> .*? ) \}
          )
      )
''', re.VERBOSE)


def parse_transition_table(s):
    """Parse a string describing a PDA.

    Return a pair (transition_table, final_states) if successful;
    otherwise raise ValueError.
    """

    table = defaultdict(dict)
    final_states = None
    for token in parse_tokens(s):
        if 'final_states' in token:
            if final_states is not None:
                raise ValueError('duplicate final state declarations')
            else:
                final_states = token.final_states
        else:
            p = token.pattern
            if (p.input, p.stack) in table[p.state]:
                raise ValueError('duplicate clauses for {}'.format(
                    (p.state, p.input, p.stack)))
            else:
                table[p.state][(p.input, p.stack)] = \
                        {(o.state, o.stack) for o in token.outputs}
    return (dict(table), final_states or frozenset())


def parse_tokens(s):
    s = re.sub(r'\s+', '', s)
    i = 0
    while i < len(s):
        m = TOKEN_RE.match(s, i)
        if m is None:
            raise ValueError('invalid syntax')
        elif m.group('final_states'):
            # Match final state declarations (e.g. '{0, 1}')
            # ``eval()`` is safe here, as the regex ensures valid input
            final_states = frozenset(eval(m.group('final_states')))
            yield PropertyDict(final_states=final_states)
        else:
            # Otherwise, it's a row of the transition table
            pattern = parse_pattern(m.group('pattern'))
            outputs = parse_outputs(m.group('output') or m.group('outputs'))
            yield PropertyDict(pattern=pattern, outputs=outputs)
        i = m.end()


def parse_pattern(s):
    """Parse the input of a transition function, written as a ``(state,
    input, stack)`` triple. The string should not contain whitespace.

    >>> parse_pattern('(123,abc,def)')
    PropertyDict(input='abc', stack='def', state=123)
    """
    m = PATTERN_RE.match(s)
    if m is None:
        raise ValueError('invalid syntax: {}'.format(s))
    else:
        return PropertyDict(
                state=int(m.group('state')),
                input=epsilon(m.group('input')),
                stack=epsilon(m.group('stack')))


def parse_outputs(s):
    return list(map(parse_output, re.split(r'(?<=\)),(?=\()', s)))


def parse_output(s):
    """Parse the output of a transition, written as a ``(state, stack)``
    pair. The input string should not contain whitespace.

    >>> parse_output('(123,abc)')
    PropertyDict(stack='abc', state=123)
    """
    m = OUTPUT_RE.match(s)
    if m is None:
        raise ValueError('invalid syntax: {}'.format(s))
    else:
        return PropertyDict(
                state=int(m.group('state')),
                stack=epsilon(m.group('stack')))


def epsilon(s):
    """If the argument contains only a lowercase 'e', return the empty
    string. Otherwise, return the string unmodified.

    This is needed because the PDA syntax doesn't let us write empty
    strings directly. As the letter 'e' somewhat approximates an
    epsilon, we use that instead.

    >>> epsilon('not an empty string')
    'not an empty string'
    >>> epsilon('e')
    ''
    """
    if s == 'e':
        return ''
    else:
        return s


class PropertyDict(dict):
    """A dictionary that lets us write ``d['key']`` as ``d.key``.

    >>> d = PropertyDict(lyra='bonbon')
    >>> d['lyra']
    'bonbon'
    >>> d.lyra
    'bonbon'
    >>> d.non_existent_attribute
    Traceback (most recent call last):
        ...
    AttributeError: non_existent_attribute
    """

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __repr__(self):
        return 'PropertyDict({})'.format(
                ', '.join('{}={!r}'.format(k, v)
                    for k, v in sorted(self.items())))
