from .core import *
from .parser import *


def parse_options(option_str):
    build_options = dict(
            input_alpha='01',
            stack_alpha='AZ',
            initial_stack='Z',
            deterministic=True,
            accept_condition=FINAL_STATE,
            )
    exec_options = dict(
            max_iterations=1000,
            max_configs=100,
            max_stack_size=100,
            )
    test_options = dict(
            use_student_answer=False,
            tests=strings_of_length(upto=9, alpha='01'),
            )

    options = {}
    options.update(build_options)
    options.update(exec_options)
    options.update(test_options)

    exec(option_str, globals(), options)

    return (project(options, build_options),
            project(options, exec_options),
            project(options, test_options))


def project(mapping, attrs):
    return {key: mapping[key] for key in attrs}


def parse(pda_str, build_options, exec_options):
    deterministic = build_options.pop('deterministic')
    table, final_states = parse_table(pda_str)
    template = Template(table=table, final_states=final_states, **build_options)
    if deterministic and not template.is_deterministic():
        raise ValueError('PDA is not deterministic')
    return lambda input: PDA(template, input, **exec_options).run()


def strings_of_length(upto, alpha):
    """Return a list of all strings up to a specified length.

    >>> strings_of_length(upto=5, alpha='a')
    ['', 'a', 'aa', 'aaa', 'aaaa', 'aaaaa']

    >>> strings_of_length(upto=2, alpha='01')
    ['', '0', '1', '00', '01', '10', '11']
    """

    def generate(size):
        if size == 0:
            yield ''
        else:
            for string in generate(size-1):
                for char in alpha:
                    yield string + char

    return [string for size in range(1+upto) for string in generate(size)]


def run_tests(run_student, run_correct, options):
    for string in options['tests']:
        try:
            student_accepts = run_student(string)
        except RuntimeError as e:
            return "On input {}: {}".format(string, e)
        except Exception as e:
            return "There's an error in the automata representation."
        correct_accepts = run_correct(string)
        if student_accepts and not correct_accepts:
            return "Input {} should be rejected.".format(string)
        elif not student_accepts and correct_accepts:
            return "Input {} should be accepted.".format(string)
    return "Good"


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        option_str = """{{ TEST.stdin | e('py') }}"""
        correct_answer = """{{ TEST.testcode | e('py') }}"""
        student_answer = """{{ STUDENT_ANSWER | e('py') }}"""
    elif len(sys.argv) == 2:
        option_str, correct_answer, student_answer = \
                open(sys.argv[1]).read().split('---')
    else:
        raise SystemExit('Usage: {} [TEST_FILE]'.format(sys.argv[0]))

    build_options, exec_options, test_options = parse_options(option_str)

    try:
        run_student = parse(student_answer, build_options, exec_options)
    except Exception as e:
        raise SystemExit(e)

    if test_options['use_student_answer']:
        run_correct = run_student
    else:
        run_correct = parse(correct_answer, build_options, exec_options)

    print(run_tests(run_student, run_correct, test_options))
