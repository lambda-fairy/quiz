from collections import defaultdict
from grako.exceptions import GrakoException

from .autogen import PDAParser, PDASemantics


__all__ = ['parse_table']


def parse_table(code):
    table = defaultdict(dict)
    for clause in parse_clauses(code):
        p = clause.pattern
        if (p.input, p.stack) in table[p.state]:
            raise ValueError('duplicate clauses for {}'.format(
                (p.state, p.input, p.stack)))
        else:
            table[p.state][(p.input, p.stack)] = \
                    {(o.state, o.stack) for o in clause.outputs}
    return [table[i] for i in range(1+max(table.keys()))]


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
        if line:
            semantics = MySemantics()
            try:
                result = PDAParser().parse(line, 'clause', semantics=semantics)
            except GrakoException:
                raise ValueError('invalid syntax')
            else:
                yield result
