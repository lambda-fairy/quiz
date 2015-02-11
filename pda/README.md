COSC261 pushdown automata verifier
==================================

You will need
-------------

* Python 3.3 or newer

* GNU Make


Quick start
-----------

Build the script with make:

    make

If successful, the script should be in `run_pda.py`.


Testing
-------

The verifier comes with automated tests.

To run these, first install the [py.test][] library:

    sudo apt-get install python3-pytest

Then:

    make test PYTEST=py.test-3

Alternatively, you can run the verifier manually:

    python3 -m pda.driver examples/palindrome.txt

More examples can be found in the `examples` directory.

[py.test]: http://pytest.org/


PDA syntax
----------

A PDA is specified through a list of clauses, each on their own line.

Each clause is in the format

    (state, input, stack) -> { (state, stack), ... }

where the states are non-negative integers, and the input and stack are
alphanumeric strings. Each transition may read an arbitrary amount of
input, and push and pop any number of symbols from the stack. If the
transition set has only one element, the braces may be omitted.

Each `(state, input, stack)` triple may only appear once. In other
words, the fragment

    (0, 0, e) -> (0, A)
    (0, 0, e) -> (1, A)

is illegal. Instead, place them all on a single line, like this:

    (0, 0, e) -> {(0, A), (1, A)}

The special token `e` stands for the empty string. To prevent confusion,
ensure your input and stack alphabets do not contain the letter E.

The initial state is always state `0`. You must declare at least one
transition from this state.

To declare final states, write a set of state numbers on its own line.
For example:

    {1, 2, 3}

This line may be anywhere in the input, but it can only appear at most
once. If omitted, the set is assumed to be empty.

Here's a PDA that matches the language `{ a^n b^n | n >= 0 }` by final
state:

    (0, a, Z) -> (0, AZ)
    (0, a, A) -> (0, AA)
    (0, e, e) -> (1, e)
    (1, b, A) -> (1, e)
    (1, e, Z) -> (2, Z)
    {2}

This PDA keeps pushing to the stack, and never terminates:

    (0, e, e) -> { (0, A), (0, Z) }


Options
-------

You can customize the simulator using various options. These options are
interpolated into the simulation code itself, so you have the full
syntax of Python at your disposal.

The values given below are the defaults, which will be used if you don't
override them.


### Automaton options

    input_alpha = '01'
    stack_alpha = 'AZ'

Input and stack alphabet. If you don't provide your own test cases (see
below), the simulator will generate its own tests from the input
alphabet.

    initial_stack = ''

Initial contents of the stack. The top element is first, as per
convention.

    deterministic = True

Whether to enforce that the automaton is deterministic. If True, any
answer that is not deterministic per [this definition][1] will be
rejected.

[1]: https://en.wikipedia.org/wiki/Deterministic_pushdown_automaton#Formal_definition

    accept_condition = FINAL_STATE

Whether to accept by empty stack (`EMPTY_STACK`), final state
(`FINAL_STATE`), or requiring both (`FINAL_STATE | EMPTY_STACK`).


### Execution limits

If the simulation breaches any of these limits, it will halt
immediately.

    max_iterations = 1000

Maximum number of steps to run the simulation.

    max_configs = 100

Maximum number of configurations to keep in memory. This is only useful
for non-deterministic PDAs, since a DPDA has only one possible
configuration at a time.

    max_stack_size = 100

Maximum number of symbols on the stack.


### Test options

    use_student_answer = False

If True, assume the student's answer is correct, effectively only
checking the syntax.

    tests = strings_of_length(upto=9, alpha=input_alpha)

A list of strings to test the PDA with. If you don't set this option,
the simulator will generate a default set automatically.
