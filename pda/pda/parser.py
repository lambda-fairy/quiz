from collections import defaultdict
from grako.exceptions import GrakoException
import re

from .autogen import PDAParser, PDASemantics


def parse_table(code):
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
        if s == 'e':
            return ''
        else:
            return s


def parse_clauses(code):
    for line in code.split('\n'):
        line = line.strip()
        if not line:
            continue
        elif is_final_states(line):
            yield False, frozenset(eval(line))
        else:
            semantics = MySemantics()
            try:
                result = PDAParser().parse(line, 'clause', semantics=semantics)
            except GrakoException:
                raise ValueError('invalid syntax')
            else:
                yield True, result


FINAL_STATES_RE = re.compile(r'\{\d+(?:,\d+)*\}$')
def is_final_states(line):
    line = re.sub(r'\s+', '', line)
    return FINAL_STATES_RE.match(line)
