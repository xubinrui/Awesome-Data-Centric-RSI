# Everything a contributor needs. `make check` is what CI runs.
PYTHON ?= python3
ENTRIES := $(wildcard data/entries/*.yaml)

.DEFAULT_GOAL := help

.PHONY: help install validate build figures fix test check new clean links stats

help:  ## show this help
	@grep -E '^[a-z-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

install:  ## install the pinned tooling
	$(PYTHON) -m pip install -r requirements.txt

validate:  ## check every entry against the rules in scripts/rsi/checks.py
	$(PYTHON) scripts/validate.py

build:  ## regenerate README, docs, schema, derived data and figures
	$(PYTHON) scripts/build.py

figures:  ## regenerate only the SVGs
	$(PYTHON) scripts/build.py --quiet

fix:  ## rewrite entry files in canonical form
	$(PYTHON) scripts/format.py
	$(PYTHON) scripts/build.py --quiet

test:  ## run the test suite
	$(PYTHON) -m pytest

check: validate test  ## everything CI runs, minus the network jobs
	$(PYTHON) scripts/format.py --check
	$(PYTHON) scripts/build.py --check
	@echo "\nall checks passed"

links:  ## verify every URL resolves (needs network)
	$(PYTHON) scripts/check_links.py --metadata

stats:  ## print the headline numbers
	@$(PYTHON) -c "import sys; sys.path.insert(0,'scripts'); \
		from rsi.entries import load_entries; from rsi.stats import summary; \
		s = summary(load_entries()); \
		print(s['entries'], 'entries ·', s['years']['min'], '-', s['years']['max']); \
		print('gaps:', ', '.join(s['coverage_gaps']) or 'none')"

new:  ## scaffold an entry: make new ARXIV=2505.03335
	@test -n "$(ARXIV)" || (echo "usage: make new ARXIV=<id>"; exit 1)
	$(PYTHON) scripts/new_entry.py --arxiv $(ARXIV)

clean:  ## remove caches
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
	rm -rf .pytest_cache
