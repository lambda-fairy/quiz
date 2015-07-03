from .core import *
from .parser import *


def parse_options(option_str):
    build_options = dict(
            input_alpha='ab',
            stack_alpha='ABCDEFGHIJKLMNOPQRSTUVWXYZ',
            initial_stack='',
            deterministic=False,
            accept_condition=FINAL_STATE | EMPTY_STACK,
            )
    exec_options = dict(
            max_iterations=1000,
            max_configs=100,
            max_stack_size=100,
            )
    test_options = dict(
            use_student_answer=False,
            tests=None,
            )

    options = {}
    options.update(build_options)
    options.update(exec_options)
    options.update(test_options)

    exec(option_str, globals(), options)

    if options['tests'] is None:
        # If the question writer didn't set any tests,
        # generate a default set from the input alphabet
        options['tests'] = \
                strings_of_length(upto=10, alpha=options['input_alpha'])

    return (project(options, build_options),
            project(options, exec_options),
            project(options, test_options))


def project(mapping, attrs):
    """Return a copy of ``mapping`` with its attributes restricted to
    those in ``attrs``.

    >>> project({'a': 1, 'b': 2}, ['a'])
    {'a': 1}
    """
    return {key: mapping[key] for key in attrs}


def parse_automaton(pda_str, build_options, exec_options):
    """Parse a string describing a PDA.

    Return a function which, when called with an input string, runs the
    PDA and returns the result.
    """
    table, final_states = parse_transition_table(pda_str)
    automaton = PDA(table=table, final_states=final_states, **build_options)
    def run(input):
        simulator = PDASimulator(automaton, input, **exec_options)
        return simulator.run()
    return run


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


def run_tests(run_student, run_correct, options):
    for string in options['tests']:
        try:
            student_accepts = run_student(string)
        except RuntimeError as e:
            return "On input {!r}: {}".format(string, e)
        except Exception as e:
            return "There's an error in the automata representation."
        correct_accepts = run_correct(string)
        if student_accepts and not correct_accepts:
            return "Input {!r} should be rejected.".format(string)
        elif not student_accepts and correct_accepts:
            return "Input {!r} should be accepted.".format(string)
    return "Good"


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        # If no command line arguments are given, assume we're on the server
        option_str = """{{ TEST.extra | e('py') }}"""
        correct_answer = """{{ QUESTION.answer | e('py') }}"""
        student_answer = """{{ STUDENT_ANSWER | e('py') }}"""
    elif len(sys.argv) == 2:
        # Read data from the given file
        option_str, correct_answer, student_answer = \
                open(sys.argv[1]).read().split('---')
    else:
        raise SystemExit('Usage: {} [TEST_FILE]'.format(sys.argv[0]))

    # Parse the option string
    build_options, exec_options, test_options = parse_options(option_str)

    # Parse the PDAs
    try:
        run_student = parse_automaton(student_answer, build_options, exec_options)
    except Exception as e:
        print(e)
        raise SystemExit

    if test_options['use_student_answer']:
        run_correct = run_student
    else:
        run_correct = parse_automaton(correct_answer, build_options, exec_options)

    # If everything's okay, run the tests
    print(run_tests(run_student, run_correct, test_options))
