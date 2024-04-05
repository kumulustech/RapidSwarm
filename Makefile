# Makefile for RapidSwarm

BUILD_DIRS = dist htmlcov
POETRY     = $(shell which poetry || echo "MISSING_POETRY")
POETRY     = $(shell which poetry || echo "MISSING_POETRY")

.PHONY: all run test clean

help:
	@echo "Make targets:"
	@echo
	@egrep '^[a-z-]+:' Makefile | sed 's/:.*//' | sed 's/^/    /'
	@echo
	@echo "First run? Try 'make prep' to install dependencies."
	@echo "...self-installing poetry is TBD!"

prep:
	$(POETRY) lock && $(POETRY) install

build:
	$(POETRY) build

show:
	$(POETRY) show --tree

test:
	$(POETRY) run pytest

format:
	find src -name '*.py' | xargs $(POETRY) run black
	find tests -name '*.py' | xargs $(POETRY) run black

fmt: format
clean:
	/bin/rm -rf $(BUILD_DIRS)

# END
