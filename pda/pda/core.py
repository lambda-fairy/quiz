from collections import namedtuple
from itertools import count, permutations


# Acceptance modes
FINAL_STATE = 1
EMPTY_STACK = 2
FINAL_STATE_AND_EMPTY_STACK = FINAL_STATE | EMPTY_STACK


# A PDA configuration: a triple containing the state, remaining input,
# and stack (top element first)
Config = namedtuple('Config', 'state input stack')


class PDA:
    """A pushdown automaton. This class deals with the static structure
    of the PDA: it stores the transition table and input/stack alphabets,
    and checks if the automaton is deterministic.

    To run a PDA on an input string, see ``PDASimulator``.
    """

    def __init__(self, input_alpha, stack_alpha, table, initial_stack,
            final_states, accept_condition, deterministic=False):

        if 0 not in table:
            raise ValueError('transition table must include at least the initial state')

        if accept_condition & FINAL_STATE and final_states is None:
            raise ValueError('missing final state declaration')

        # Check stack contains only valid symbols
        if not all(symbol in stack_alpha for symbol in initial_stack):
            raise ValueError('invalid initial stack')

        unreachable = set(table.keys())
        if final_states is not None:
            unreachable.update(final_states)
        unreachable.discard(0)  # Initial state is always reachable

        # Check transition table
        for subtable in table.values():
            for (input_prefix, stack_prefix), entries in subtable.items():
                # Check that all input patterns are in the input alphabet
                bad_symbols = [symbol for symbol in input_prefix
                        if symbol not in input_alpha]
                if bad_symbols:
                    raise ValueError(
                            '{!r} is not in the input alphabet'
                            .format(bad_symbols[0]))
                # Check that all stack patterns are in the stack alphabet
                bad_symbols = [symbol for symbol in stack_prefix
                        if symbol not in stack_alpha]
                if bad_symbols:
                    raise ValueError(
                            '{!r} is not in the stack alphabet'
                            .format(bad_symbols[0]))
                for state, stack in entries:
                    # If there is a transition leading to some state, then that
                    # state is (probably) reachable
                    unreachable.discard(state)
                    if not all(symbol in stack_alpha for symbol in stack):
                        raise ValueError('invalid stack symbols: {!r}'.format(stack))

        # Check for states which have no transitions going into them
        if unreachable:
            raise ValueError('states {} are unreachable'.format(unreachable))

        # If everything's okay, construct the object
        self.input_alpha = input_alpha
        self.stack_alpha = stack_alpha
        self.table = table
        self.initial_stack = initial_stack
        self.final_states = final_states
        self.accept_condition = accept_condition

        if deterministic and not self.is_deterministic():
            raise ValueError('PDA is not deterministic')

    def is_deterministic(self):
        """Return True if the PDA is deterministic."""
        for subtable in self.table.values():
            for items_i, items_j in permutations(subtable.items(), 2):
                (input_i, stack_i), entries_i = items_i
                (input_j, stack_j), entries_j = items_j
                if (overlap(input_i, input_j) and overlap(stack_i, stack_j) and
                        len(entries_i) + len(entries_j) > 1):
                    return False
        return True


class PDASimulator:
    """Simulates a PDA over a specific input string.

    Use ``run()`` to drive the PDA to completion, or ``step()`` to run
    it one step at a time.
    """

    def __init__(self, automaton, input,
            max_iterations=None, max_configs=None, max_stack_size=None):
        """Construct a simulator with PDA ``automaton`` and input string
        ``input``."""

        # Check input contains only valid symbols
        if not all(symbol in automaton.input_alpha for symbol in input):
            raise ValueError('invalid input')

        self.table = automaton.table
        self.final_states = automaton.final_states
        self.accept_condition = automaton.accept_condition

        # Initial state is assumed to be q0
        self.data = frozenset({Config(0, input, automaton.initial_stack)})

        self.max_iterations = max_iterations
        self.max_configs = max_configs
        self.max_stack_size = max_stack_size

    def __repr__(self):
        return '<PDASimulator {}>'.format(set(map(tuple, self.data)))

    def run(self):
        """Run the PDA to completion.

        Return True if it accepts, False if it rejects, or raise
        RuntimeError if it breaks any execution limit.
        """

        iterations = range(self.max_iterations) if self.max_iterations else count()
        for i in iterations:
            if self.accepts():
                return True
            if self.rejects():
                return False
            self.step()
        else:
            raise RuntimeError('iteration limit reached (is there an infinite loop?)')

    def accepts(self):
        """Return True if the PDA is in an accepting state."""
        if self.accept_condition & FINAL_STATE and not self.is_final_state():
            return False
        if self.accept_condition & EMPTY_STACK and not self.is_empty_stack():
            return False
        return True

    def rejects(self):
        """Return True if we can guarantee the PDA will never reach an
        accepting state."""
        return not self.data

    def is_final_state(self):
        """Return True if the PDA is in a final state."""
        return any(not input and state in self.final_states for state, input, _ in self.data)

    def is_empty_stack(self):
        """Return True if the PDA has an empty stack."""
        return any(not input and not stack for _, input, stack in self.data)

    def step(self):
        """Advance the automaton by a single transition."""
        new_data = self._next_configs()
        if self.max_configs:
            new_data = limit_len(new_data, self.max_configs, 'too many configurations')
        new_data = frozenset(new_data)
        if (self.max_stack_size and
                any(len(config.stack) > self.max_stack_size for config in new_data)):
            raise RuntimeError('stack too large')
        self.data = new_data

    def _next_configs(self):
        """Generate all the configurations that can be reached by a
        single transition."""
        for state, input, stack in self.data:
            subtable = self.table.get(state, {})
            for (input_prefix, stack_prefix), entries in subtable.items():
                if (input.startswith(input_prefix) and
                        stack.startswith(stack_prefix)):
                    for next_state, next_stack in entries:
                        yield Config(
                                next_state,
                                input[len(input_prefix):],
                                next_stack+stack[len(stack_prefix):])


def overlap(a, b):
    """Determine if one string is a prefix of the other."""
    return a.startswith(b) or b.startswith(a)


def limit_len(iterable, limit, error='too many items'):
    """Raise an exception when the iterable has too many elements."""
    for index, elem in enumerate(iterable):
        if index == limit:
            raise RuntimeError(error)
        else:
            yield elem
