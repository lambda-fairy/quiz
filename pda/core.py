#!/usr/bin/env python3

from collections import namedtuple
from itertools import permutations


# Acceptance modes
FINAL_STATE = 1
EMPTY_STACK = 2
FINAL_STATE_AND_EMPTY_STACK = FINAL_STATE | EMPTY_STACK


# A PDA configuration: a triple containing the state, remaining input,
# and stack (top element first)
Datum = namedtuple('Datum', 'state input stack')


class Template:
    def __init__(self, input_alpha, stack_alpha, table, initial_stack,
            final_states, accept_condition):

        if not table:
            raise ValueError('transition table must declare at least one state')

        # Check stack contains only valid symbols
        if not all(symbol in stack_alpha for symbol in initial_stack):
            raise ValueError('invalid initial stack')

        # Check final states
        for state in final_states:
            if not (0 <= state < len(table)):
                raise ValueError('invalid final state: {!r}'.format(state))

        # Check transition table
        for subtable in table:
            for (input_prefix, stack_prefix), entries in subtable.items():
                if not all(symbol in input_alpha for symbol in input_prefix):
                    raise ValueError('{!r} is not in the input alphabet'.format(input_symbol))
                if not all(symbol in stack_alpha for symbol in stack_prefix):
                    raise ValueError('{!r} is not in the stack alphabet'.format(stack_symbol))
                for state, stack in entries:
                    if not (0 <= state < len(table)):
                        raise ValueError('invalid state number: {!r}'.format(state))
                    if not all(symbol in stack_alpha for symbol in stack):
                        raise ValueError('invalid stack symbols: {!r}'.format(stack))

        # If everything's okay, construct the object
        self.input_alpha = input_alpha
        self.stack_alpha = stack_alpha
        self.table = table
        self.initial_stack = initial_stack
        self.final_states = final_states
        self.accept_condition = accept_condition

    def is_deterministic(self):
        """Return True iff the PDA is deterministic."""
        for subtable in self.table:
            for items_i, items_j in permutations(subtable.items(), 2):
                (input_i, stack_i), entries_i = items_i
                (input_j, stack_j), entries_j = items_j
                if (overlap(input_i, input_j) and overlap(stack_i, stack_j) and
                        len(entries_i) + len(entries_j) > 1):
                    return False
        return True


class PDA:
    def __init__(self, template, input):
        # Check input contains only valid symbols
        if not all(symbol in template.input_alpha for symbol in input):
            raise ValueError('invalid input')

        self.table = template.table
        self.final_states = template.final_states
        self.accept_condition = template.accept_condition

        # Initial state is assumed to be q0
        self.data = frozenset({Datum(0, input, template.initial_stack)})

    def __repr__(self):
        return '<PDA {}>'.format(set(map(tuple, self.data)))

    def run(self, max_iterations=100):
        for iteration in range(max_iterations):
            if self.accepts():
                return True
            if self.rejects():
                return False
            self.step()
        else:
            raise RuntimeError('iteration limit reached (is there an infinite loop?)')

    def accepts(self):
        """Return True iff the PDA is in an accepting state."""
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
        """Return True iff the PDA is in a final state."""
        return any(not input and state in self.final_states for state, input, _ in self.data)

    def is_empty_stack(self):
        """Return True iff the PDA has an empty stack."""
        return any(not input and len(stack) == 0 for _, input, stack in self.data)

    def step(self):
        """Advance the automaton by a single transition."""
        self.data = frozenset(self._step_generator(self.table, self.data))

    @staticmethod
    def _step_generator(table, data):
        for state, input, stack in data:
            subtable = table[state]
            for (input_prefix, stack_prefix), entries in subtable.items():
                if (input.startswith(input_prefix) and
                        stack.startswith(stack_prefix)):
                    for next_state, next_stack in entries:
                        yield Datum(
                                next_state,
                                input[len(input_prefix):],
                                next_stack+stack[len(stack_prefix):])


def overlap(a, b):
    """Determine if one string is a prefix of the other."""
    return a.startswith(b) or b.startswith(a)
