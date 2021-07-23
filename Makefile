MAKEFLAGS += --no-print-directory

# Do not remove this block. It is used by the 'help' rule when
# constructing the help output.
# help:
# help: Makefile help
# help:

# help: compile-requirements           - compile soft requirements to hard versioned requirements
# .PHONY: compile-requirements
# compile-requirements:
# 	pip-compile requirements.in > requirements.txt

# help: install                        - install dependencies
.PHONY: install
install: install-all

# help: install-all                    - install all dependencies
.PHONY: install-all
install-all:
	@poetry install

# help: install-base                   - install base dependencies
.PHONY: install-base
install-base:
	@poetry install --no-dev

# help: install-testing                - install test dependencies
.PHONY: install-testing
install-testing:
	@poetry install

# help: install-linting                - install linting dependencies
.PHONY: install-linting
install-linting:
	@poetry install

# help: help                           - display this makefile's help information
.PHONY: help
help:
	@grep "^# help\:" Makefile | grep -v grep | sed 's/\# help\: //' | sed 's/\# help\://'

# help: test                           - run tests
.PHONY: test
test:
	@poetry run pytest -v -s

# help: lint                           - run lint
.PHONY: lint
lint:
	@poetry run flake8 src/ tests/ examples/
	@poetry run isort src/ tests/ examples/ --check-only --df --profile=black
	@poetry run black src/ tests/ examples/ --check --diff

# help: mypy                           - run typechecking
.PHONY: mypy
mypy:
	@poetry run mypy src/

# help: format                         - perform code style format
.PHONY: format
format:
	@poetry run isort src/ tests/ examples/ --profile=black
	@poetry run black src/ tests/ examples/

# Keep these lines at the end of the file to retain nice help
# output formatting.
# help:
