from copy import copy

from pda import PDA


# This PDA matches the language { 0^n 1^n | n : N }
pda_0n_1n = PDA(
        list('01'),
        list('AZ'),
        [
            {
                ('0', 'Z'): {(0, 'AZ')},
                ('0', 'A'): {(0, 'AA')},
                (None, 'Z'): {(1, 'Z')},
                (None, 'A'): {(1, 'A')},
                },
            {
                ('1', 'A'): {(1, '')},
                (None, 'Z'): {(2, 'Z')},
                },
            {},
            ],
        'Z',
        {2})


def is_0n_1n(s):
    return s.count('0') == s.count('1') and '10' not in s


def binary_strings(max_length=10):
    """Yield all binary strings up to a specified length inclusive.

    >>> list(binary_strings(max_length=2))
    ['', '0', '1', '00', '01', '10', '11']
    """
    yield ''
    for size in range(1, 1+max_length):
        for i in range(2**size):
            yield '{:b}'.format(i).rjust(size, '0')


def test_deterministic():
    assert not pda_0n_1n.is_deterministic()


def test_matching():
    for s in binary_strings():
        pda = copy(pda_0n_1n)
        pda.feed(s)
        assert is_0n_1n(s) == pda.is_final_state()
