#!/usr/bin/env python3
import re
import sys


def ensure(b, s="assertion failed"):
    if not b:
        raise Exception(s)


def sepby(s, sep):
    return r'(' + s + r')((' + sep + r')(' + s + r'))*'


def parse(answer):
    '''Parse a TM from answer and return the transition table.
       Raise an exception if this cannot be done.'''
    # error constants
    lexical_error = "There's a lexical error in the TM representation."
    syntactic_error = "There's a syntactic error in the TM representation."
    structural_error = "There's a structural error in the TM representation."
    # regular expressions for syntax
    tm_lexical = re.compile(r'^[0-9arLNR_,()\[\]]*$')
    entry_syntax = r'\((a|r|[0-9]+),[0-9_],[LNR]\)'
    row_syntax = r'\[' + sepby(entry_syntax, ',') + r'\]'
    matrix_syntax = r'\[' + sepby(row_syntax, ',') + r'\]'
    tm_syntax = re.compile(r'^' + matrix_syntax + r'$')
    #
    answer = answer.strip().replace('\n','').replace('\t','').replace(' ','')
    ensure(tm_lexical.match(answer), lexical_error)
    ensure(tm_syntax.match(answer), syntactic_error)
    answer = answer.replace('a','-1').replace('r','-2').replace('L','-1').replace('N','0').replace('R','1').replace('_','-1')
    try:
        table = eval(answer)
    except Exception:
        raise Exception(syntactic_error)
    # check that the table and final states represent a TM
    number_of_states = len(table)
    ensure(1 <= number_of_states, structural_error)
    number_of_symbols = len(table[0])
    ensure(1 <= number_of_symbols, structural_error)
    for row in table:
        ensure(len(row) == number_of_symbols, structural_error)
        for (state, symbol, direction) in row:
            ensure(-2 <= state < number_of_states, structural_error)
            ensure(-1 <= symbol < number_of_symbols-1, structural_error)
            ensure(-1 <= direction <= 1, structural_error)
    return table


def strings_of_length(upto, alpha):
    """Return a list of all strings up to a specified length.

    >>> strings_of_length(upto=5, alpha='a')
    ['', 'a', 'aa', 'aaa', 'aaaa', 'aaaaa']

    >>> strings_of_length(upto=2, alpha='01')
    ['', '0', '1', '00', '01', '10', '11']
    """

    result = buffer = ['']
    for size in range(1, 1+upto):
        buffer = [string+char for string in buffer for char in alpha]
        result.extend(buffer)
    return result


def simulate(table, right, max_steps=500):
    state = 0
    left = ''
    while state >= 0 and max_steps > 0:
        max_steps -= 1
        symbol = '_' if len(right) == 0 else right[0]
        read = -1 if symbol == '_' else int(symbol)
        assert read < len(table[state]) - 1
        state, write, move = table[state][read]
        symbol = '_' if write == -1 else str(write)
        right = symbol + right[1:]
        if move == -1:
            symbol = '_' if len(left) == 0 else left[-1]
            right = symbol + right
            left = left[:-1]
        elif move == 1:
            symbol = '_' if len(right) == 0 else right[0]
            left = left + symbol
            right = right[1:]
    if max_steps <= 0:
        return None
    return (state, (left + right).strip('_'))


def parse_options(option_str):
    """Parse an option string into a dictionary. The string is
    interpreted as Python code."""
    options = dict(
            ignore_output=False,
            use_student_answer=False,
            input_alpha='01'
            )
    exec(option_str, globals(), options)
    if 'tests' not in options:
        options['tests'] = strings_of_length(upto=9, alpha=options['input_alpha'])
        # Test long strings
        for char in input_alpha:
            options['tests'].append(30*char)
        # Test a few "random" strings
        # We initialize the generator with a constant seed, to ensure
        # consistency between runs
        generator = Random(0)
        for i in range(10):
            s = ''.join(generator.choice(input_alpha) for _ in range(30))
            options['tests'].append(s)
    return options


def run_tests(student_table, correct_table, options):
    for string in options['tests']:
        try:
            student_answer = simulate(student_table, string)
        except Exception:
            return "There's an error in the automata representation."
        correct_answer = simulate(correct_table, string)
        if student_answer != correct_answer:
            if student_answer is None:
                return "TM takes too many steps for input '" + string + "'."
            elif correct_answer is None:
                return "TM should not terminate for input '" + string + "'."
            elif student_answer[0] == -1 and correct_answer[0] == -2:
                return "Input '" + string + "' should be rejected."
            elif student_answer[0] == -2 and correct_answer[0] == -1:
                return "Input '" + string + "' should be accepted."
            elif not options['ignore_output'] and student_answer[1] != correct_answer[1]:
                return "TM computes the wrong result for input '" + string + "'."
    return "Good"


if __name__ == '__main__':
    if len(sys.argv) == 1:
        # On the quiz server, these string constants will be replaced
        # with the real input
        option_str = """{{ TEST.stdin | e('py') }}"""
        correct_answer = """{{ TEST.testcode | e('py') }}"""
        student_answer = """{{ STUDENT_ANSWER | e('py') }}"""
    elif len(sys.argv) == 2:
        # Read input from a file, for testing
        option_str, correct_answer, student_answer = \
                open(sys.argv[1]).read().split('---')
    else:
        raise SystemExit('Usage: {} [TEST_FILE]'.format(sys.argv[0]))

    options = parse_options(option_str)

    try:
        student_table = parse(student_answer)
    except Exception as e:
        raise SystemExit(e)

    if options['use_student_answer']:
        correct_table = student_table
    else:
        correct_table = parse(correct_answer)

    print(run_tests(student_table, correct_table, options))
