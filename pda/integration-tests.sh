#!/bin/sh

# Run the final script (run_pda.py) with a few examples, just to verify
# that everything works as expected.
#
# If you come up with more test cases, consider adding them to the
# bottom of this file.

status=0

test_example() {
    input="$1"
    expected="$2"
    echo -n "test $input ... "
    output="$(./run_pda.py "examples/$input.txt")"
    if [ "$output" = "$expected" ]
    then
        echo 'ok'
    else
        echo 'FAILED'
        echo "\t(expected \"$expected\", got \"$output\")"
        status=1
    fi
}

test_example palindrome 'Good'
test_example incorrect "Input 'bb' should be accepted."

exit $status
