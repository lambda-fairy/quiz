#!/usr/bin/env python3

from collections import namedtuple


# The instantaneous description: a triple containing the state, any
# remaining input, and the stack (top element first)
Datum = namedtuple('Datum', ['state', 'input', 'stack'])


class PDA:
    def __init__(self, input_alpha, stack_alpha, table, input, stack, final_states):

        if not all(symbol in input_alpha for symbol in input):
            raise ValueError('invalid input')
        if not all(symbol in stack_alpha for symbol in stack):
            raise ValueError('invalid initial stack')

        if not table:
            raise ValueError('transition table must declare at least one state')

        # Check final states
        for state in final_states:
            if not (0 <= state < len(table)):
                raise ValueError('invalid final state: {!r}'.format(state))

        # Check transition table
        for subtable in table:
            for (input_symbol, stack_symbol), entries in subtable.items():
                if not (input_symbol is None or input_symbol in input_alpha):
                    raise ValueError('{!r} is not in the input alphabet'.format(input_symbol))
                if not (stack_symbol in stack_alpha):
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
        self.final_states = final_states
        self.recursion_limit = recursion_limit

        # Initial state is assumed to be q0
        self.data = self._epsilon_closure({Datum(0, initial_stack)})

    def __repr__(self):
        return '<PDA {}>'.format(set(map(tuple, self.data)))

    def is_deterministic(self):
        """Return True iff the PDA is deterministic."""
        for subtable in self.table:
            for (input_symbol, stack_symbol), entries in subtable.items():
                if len(entries) > 1:
                    # If there is more than one possible transition,
                    # then it must be nondeterministic
                    return False
                if (input_symbol is not None and entries and
                        subtable.get((None, stack_symbol))):
                    # If there are transitions for both empty input AND
                    # non-empty input, then it is nondeterministic
                    return False
        return True

    def is_final_state(self):
        """Return True iff the PDA is in a final state."""
        return any(state in self.final_states for state, _ in self.data)

    def is_empty_stack(self):
        """Return True iff the PDA has an empty stack."""
        return any(len(stack) == 0 for _, stack in self.data)

    def feed(self, input_string):
        """Feed the given string into the automaton."""
        for input_symbol in input_string:
            self.step(input_symbol)

    def step(self, input_symbol):
        """Step the automaton with the specified input symbol."""
        if input_symbol is None:
            raise ValueError('input symbol cannot be None')
        data = self.data
        data = self._single_step(data, input_symbol)
        data = self._epsilon_closure(data)
        self.data = data

    def _epsilon_closure(self, data):
        """
        Compute the epsilon closure, that is, the set of all states that
        can be reached without consuming input.
        """
        # Do a breadth-first traversal of the state graph
        frontier = data
        visited = set(frontier)
        for iteration in range(self.recursion_limit):
            # Find all the states we can reach by a single transition
            frontier = self._single_step(frontier, None)
            # Remove any states we've already visited
            frontier.difference_update(visited)
            if not frontier:
                return visited
            else:
                visited.update(frontier)
        else:
            raise ValueError(
                    'recursion limit reached (is there an infinite loop?)')

    def _single_step(self, data, input_symbol):
        return set(self._single_step_generator(data, input_symbol))

    def _single_step_generator(self, data, input_symbol):
        for state, stack in data:
            try:
                stack_symbol = stack[0]
            except IndexError:
                # Our model doesn't handle empty stacks
                continue

            subtable = self.table[state]
            try:
                entries = subtable[(input_symbol, stack_symbol)]
            except KeyError:
                continue

            for next_state, next_stack in entries:
                yield Datum(next_state, next_stack+stack[1:])
