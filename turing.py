import re
import sys

options = """{{ TEST.stdin | e('py') }}"""
options = options.strip().split('\n')

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
    except:
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

student_answer = """{{ STUDENT_ANSWER | e('py') }}"""
try:
    student_table = parse(student_answer)
except Exception as e:
    print(e)
    sys.exit()

if "use student answer" in options:
    correct_answer = student_answer
    correct_table = student_table
else:
    correct_answer = """{{ TEST.testcode | e('py') }}"""
    correct_table = parse(correct_answer)

def unary_strings_of_length(lo, hi=None):
    if hi == None:
        hi = lo
    result = []
    for length in range(lo, hi+1):
        result.append('0'*length)
    return result

def binary_strings_of_length(lo, hi=None):
    if hi == None:
        hi = lo
    result = []
    for length in range(hi+1):
        if length == 0:
            current = ['']
        else:
            current = [ s+b for b in ['0','1'] for s in current ]
        if lo <= length and length <= hi:
            result += current
    return result

tests_options = [option[8:] for option in options if option.startswith("tests = ")]
if len(tests_options) != 0:
    tests = eval(tests_options[0])
elif "use student answer" in options:
    tests = unary_strings_of_length(0, 9)
else:
    tests = binary_strings_of_length(0, 9) + [
        "111111111111111111111111111",
        "000000000000000000000000000",
        "000000000000000000000000100",
        "000001010011100101110111",
        "111110101100011010001000"
    ]

def simulate(table, right, max_steps=500):
    state = 0
    left = ''
    while state >= 0 and max_steps > 0:
        max_steps -= 1
        symbol = '_' if len(right) == 0 else right[0]
        read = -1 if symbol == '_' else int(symbol)
        assert(read < len(table[state])-1)
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
    return (state,(left + right).strip('_'))

result = "Good"
for string in tests:
    try:
        student_answer = simulate(student_table, string)
    except:
        result = "There's an error in the automata representation."
        break
    correct_answer = simulate(correct_table, string)
    if student_answer != correct_answer:
        if student_answer == None:
            result = "TM takes too many steps for input '" + string + "'."
            break
        elif correct_answer == None:
            result = "TM should not terminate for input '" + string + "'."
            break
        elif student_answer[0] == -1 and correct_answer[0] == -2:
            result = "Input '" + string + "' should be rejected."
            break
        elif student_answer[0] == -2 and correct_answer[0] == -1:
            result = "Input '" + string + "' should be accepted."
            break
        elif "ignore output" not in options and student_answer[1] != correct_answer[1]:
            result = "TM computes the wrong result for input '" + string + "'."
            break
        else:
            pass
print(result)

