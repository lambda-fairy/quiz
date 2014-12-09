GRAKO := grako
PYTEST := py.test

parsers: pda/autogen.py

pda/autogen.py: pda/pda.grako
	$(GRAKO) $< --output $@ --name PDA

test: parsers
	$(PYTEST) --verbose --ignore=env --doctest-modules

.PHONY: parsers test
