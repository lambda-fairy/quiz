GRAKO := grako
PYTEST := py.test

all: pda/autogen.py

pda/autogen.py: pda/pda.grako
	$(GRAKO) $< --output $@ --name PDA

test:
	$(PYTEST) --verbose --ignore=env

.PHONY: all test
