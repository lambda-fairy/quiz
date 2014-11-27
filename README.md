COSC261 quiz checker
====================

You will need
-------------

* Python 3.3 or newer

* GNU Make

* [pip][], for installing extra packages

* [virtualenv][], to prevent conflicts with other software (optional)


Quick start
-----------

Set up a [sandbox][virtualenv] (optional)

    virtualenv --python=python3 env
    source env/bin/activate

Install dependencies

    pip install -r requirements.txt

Generate parsers

    make

Run tests

    make test


[pip]: https://pip.pypa.io
[virtualenv]: http://docs.python-guide.org/en/latest/dev/virtualenvs/
