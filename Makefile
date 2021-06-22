MAKEFLAGS += --no-print-directory

# Do not remove this block. It is used by the 'help' rule when
# constructing the help output.
# help:
# help: Makefile help
# help:

# help: compile-requirements           - compile soft requirements to hard versioned requirements
.PHONY: compile-requirements
compile-requirements:
	pip-compile requirements.in > requirements.txt

# help: install                        - install dependencies
.PHONY: install
install: install-base

# help: install-base                   - install base dependencies
.PHONY: install-base
install-base:
	pip install -r requirements.txt

# help: install-tests                  - install test dependencies
.PHONY: install-tests
install-tests:
	pip install -r tests/requirements-testing.txt

# help: help                           - display this makefile's help information
.PHONY: help
help:
	@grep "^# help\:" Makefile | grep -v grep | sed 's/\# help\: //' | sed 's/\# help\://'

# help: test                           - run tests
.PHONY: test
test:
	@python -m unittest discover tests/

# help: lint                           - run lint
.PHONY: lint
lint:
	@flake8 src/ tests/
	@isort src/ tests/ --check-only --df --profile=black
	@black src/ tests/ --check --diff

# help: mypy                           - run typechecking
.PHONY: mypy
mypy:
	@mypy src/

# help: format                         - perform code style format
.PHONY: format
format:
	@isort src/ tests/ --profile=black
	@black src/ tests/

# Keep these lines at the end of the file to retain nice help
# output formatting.
# help:
