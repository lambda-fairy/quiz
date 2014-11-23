#!/usr/bin/env python3

from collections import namedtuple


# A pair containing a state label and a stack (top element first)
Datum = namedtuple('Datum', ['state', 'stack'])


class PDA:
    def __init__(self, input_alpha, stack_alpha, states, initial_stack,
            final_states, recursion_limit=100):

        if not states:
            raise ValueError('transition table must declare at least one state')

        self.input_alpha = input_alpha
        self.stack_alpha = stack_alpha
        self.states = states
        self.final_states = final_states
        self.recursion_limit = recursion_limit

        # Initial state is assumed to be q0
        self.data = self._epsilon_closure({Datum(0, initial_stack)})

    def __repr__(self):
        return '<PDA {}>'.format(set(map(tuple, self.data)))

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

            table = self.states[state]
            try:
                next_state, next_stack = table[(input_symbol, stack_symbol)]
            except KeyError:
                continue

            yield Datum(next_state, next_stack+stack[1:])


# This PDA matches the language { 0^n 1^n | n : N }
test_pda = PDA(
        list('01'),
        list('AZ'),
        [
            {
                ('0', 'Z'): (0, 'AZ'),
                ('0', 'A'): (0, 'AA'),
                (None, 'Z'): (1, 'Z'),
                (None, 'A'): (1, 'A'),
                },
            {
                ('1', 'A'): (1, ''),
                (None, 'Z'): (2, 'Z'),
                },
            {},
            ],
        'Z',
        {2})

test_func = lambda s: s.count('0') == s.count('1') and '10' not in s


if __name__ == '__main__':
    # Testing procedure yay
    from copy import copy
    for size in range(10):
        for i in range(1 << size):
            s = '{:b}'.format(i).rjust(size, '0')
            pda = copy(test_pda)
            pda.feed(s)
            assert test_func(s) == pda.is_final_state(), s
    print('It works!')
