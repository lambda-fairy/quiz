from collections import defaultdict
from grako.exceptions import GrakoException
import re

from .autogen import PDAParser, PDASemantics


def parse_transition_table(code):
    """Parse a string describing a PDA.

    Return a pair (transition_table, final_states) if successful;
    otherwise raise ValueError.
    """

    table = defaultdict(dict)
    final_states = None
    for is_transition, clause in parse_clauses(code):
        if is_transition:
            p = clause.pattern
            if (p.input, p.stack) in table[p.state]:
                raise ValueError('duplicate clauses for {}'.format(
                    (p.state, p.input, p.stack)))
            else:
                table[p.state][(p.input, p.stack)] = \
                        {(o.state, o.stack) for o in clause.outputs}
        else:
            if final_states is not None:
                raise ValueError('duplicate final state declarations')
            else:
                final_states = clause
    return (dict(table), final_states or frozenset())


class MySemantics(PDASemantics):
    def number(self, s):
        return int(s)

    def word(self, s):
        # Treat 'e' ("epsilon") as a synonym for an empty string
        if s == 'e':
            return ''
        else:
            return s


def parse_clauses(code):
    for line in code.split('\n'):
        line = line.strip()
        if not line:
            # Ignore empty lines
            continue
        elif is_final_states(line):
            # Match final state declarations (e.g. '{0, 1}')
            yield False, frozenset(eval(line))
        else:
            # Otherwise, parse it as a clause of the transition table
            semantics = MySemantics()
            try:
                result = PDAParser().parse(line, 'clause', semantics=semantics)
            except GrakoException:
                raise ValueError('invalid syntax')
            else:
                yield True, result


FINAL_STATES_RE = re.compile(r'\{(?:\d+(?:,\d+)*)?\}$')
def is_final_states(line):
    """Return True if the string is a final state declaration.

    >>> is_final_states('{}')
    True
    >>> is_final_states('{1, 2, 3}')
    True
    >>> is_final_states('Oatmeal, are you crazy?')
    False
    """

    line = re.sub(r'\s+', '', line)
    return bool(FINAL_STATES_RE.match(line))
