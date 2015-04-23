EGREP := grep -E
PYTEST := py.test
SED := sed

MODULES := pda/core.py pda/parser.py pda/driver.py

IMPORTS_REGEX := '^[[:space:]]*from[[:space:]]+\.'

all: run_pda.py

# Merge all the modules into a single file (hacky!)
run_pda.py: $(MODULES)
	echo '#!/usr/bin/env python3' > $@
	$(EGREP) --invert-match --no-filename $(IMPORTS_REGEX) $+ >> $@
	chmod +x $@

test: $(MODULES) test_pda.py
	$(PYTEST) --verbose --doctest-modules $+

clean:
	rm -f run_pda.py

.PHONY: all test clean
