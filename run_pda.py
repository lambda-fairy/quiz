from pda import *


def parse_options(option_str):
    construction = dict(
            input_alpha='01',
            stack_alpha='AZ',
            initial_stack='Z',
            final_states=frozenset(),
            deterministic=True,
            accept_condition=FINAL_STATE,
            )
    execution = dict(
            max_iterations=1000,
            max_configs=100,
            max_stack_size=100,
            )
    testing = dict(
            use_student_answer=False,
            tests=strings_of_length(upto=9),
            )

    options = {}
    options.update(construction)
    options.update(execution)
    options.update(testing)

    exec(option_str, globals(), options)

    return (project(options, construction),
            project(options, execution),
            project(options, testing))


def project(mapping, attrs):
    return {key: mapping[key] for key in attrs}


def parse(pda_str):
    try:
        option_str, table_str = pda_str.split('---')
    except ValueError:
        option_str, table_str = '', pda_str
    construction_options, execution_options, testing_options = parse_options(option_str)
    deterministic = construction_options.pop('deterministic')
    table = parse_table(table_str)
    template = Template(table=table, **construction_options)
    if deterministic and not template.is_deterministic():
        raise ValueError('PDA is not deterministic')
    return (lambda input: PDA(template, input, **execution_options).run(),
            testing_options)


def strings_of_length(upto, alpha='01'):
    if upto < 0:
        raise ValueError('cannot build strings of negative length')
    elif upto == 0:
        yield ''
    else:
        strings = list(strings_of_length(upto-1, alpha))
        yield from strings
        for string in strings:
            for char in alpha:
                yield char + alpha


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        pda_str = sys.stdin.read()
    elif len(sys.argv) == 2:
        pda_str = open(sys.argv[1]).read()
    else:
        raise SystemExit('USAGE: {} [FILE]'.format(sys.argv[0]))
    (run, testing_options) = parse(pda_str)
    # TODO: do some better testing here
    print('Accepted' if run('000111') else 'Rejected')
