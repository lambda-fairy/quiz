EGREP := grep -E
GRAKO := grako
PYTEST := py.test
SED := sed

IMPORTS_REGEX := '^[[:space:]]*from[[:space:]]+(__future__|\.|pda)'

all: run_pda.py

run_pda.py: pda/core.py pda/autogen.py pda/parser.py pda/driver.py
	echo '#!/usr/bin/env python3' > $@
	$(EGREP) --invert-match --no-filename $(IMPORTS_REGEX) $+ >> $@
	chmod +x $@

parsers: pda/autogen.py

pda/autogen.py: pda/autogen_orig.py
	$(SED) --quiet --expression='/^if __name__ ==/q; p' $< > $@

pda/autogen_orig.py: pda/pda.grako
	$(GRAKO) $< --output $@ --name PDA

test: parsers
	$(PYTEST) --verbose --ignore=env --doctest-modules

.PHONY: all parsers test
