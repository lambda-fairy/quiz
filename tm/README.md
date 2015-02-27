COSC261 Turing machine verifier
===============================

Options
-------

You can customize this simulator using various options. These options
are interpolated into the simulation code itself, so you have the full
syntax of Python at your disposal.

The values given below are the defaults, which will be used if you don't
override them.


### List of options

    use_student_answer = False

If True, assume the student's answer is correct, effectively only
checking the syntax.

    tests = strings_of_length(upto=9, alpha=input_alpha)

A list of strings to test the Turing machine with. If you don't set this
option, the simulator will generate a default set from `input_alpha`.

    input_alpha = '01'

The input alphabet. Note that this is used only for generating test
cases; the machine itself can always use any alphanumeric symbol for its
intermediate states.
