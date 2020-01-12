VENV = . ./venv/bin/activate;
PKG_DIR = src
TEST_DIR = tests
PKG_NAME = pydecor
SRC_FILES = *.py $(PKG_DIR) $(TEST_DIR)
TEST = pytest \
	--cov-config=setup.cfg \
	--cov=$(PKG_NAME) \
	--doctest-modules \
	$(PKG_DIR) \
	$(TEST_DIR)

.PHONY: bench build clean distribute fmt lint test

all: fmt lint test

venv: venv/bin/activate
venv/bin/activate: setup.py
	python3 -m venv venv
	$(VENV) pip install -e .[dev]
	touch venv/bin/activate


venv-clean:
	rm -rf venv


venv-refresh: venv-clean venv
	$(VENV) pip install -e .[dev]


venv-update: venv
	$(VENV) pip install -e .[dev]


build: venv build-clean
	$(VENV) python setup.py sdist bdist_wheel


build-clean:
	rm -rf build dist
	rm -rf src/*.egg-info

clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

# Requires VERSION to be set on the CLI or in an environment variable,
# e.g. make VERSION=1.0.0 distribute
distribute: build
	$(VENV) scripts/check_ready_to_distribute.py $(VERSION)
	git tag -s "v$(VERSION)"
	git push --tags

SRC_INPUTS := $(shell find src/pydecor -name \*.py -print)
DOC_INPUTS := $(shell find docs -name \*.rst -print)
docs: venv docs/conf.py docs/Makefile $(DOC_INPUTS) $(SRC_INPUTS)
	rm -rf docs/_build
	$(VENV) pip install -r docs/requirements.txt
	$(VENV) sphinx-apidoc -o docs src/pydecor --separate -f
	make text --directory=docs
	make html --directory=docs
	touch docs/

# DOC_INPUTS := $(shell find src/pydecor -name \*.py -print)
# docs/index.rst: $(DOC_INPUTS) docs/conf.py docs-clean
# 	rm -rf docs/_build
# 	$(VENV) pip install -r docs/requirements.txt
# 	$(VENV) sphinx-apidoc -o docs src/pydecor --separate -f
# 	make text --directory=docs
# 	make html --directory=docs
# 	touch docs/index.rst

fmt: venv
	$(VENV) black $(SRC_FILES)

lint: venv
	$(VENV) black --check $(SRC_FILES)
	# $(VENV) pydocstyle $(SRC_FILES)
	# $(VENV) flake8 $(SRC_FILES)
	# $(VENV) pylint --errors-only $(SRC_FILES)
	# $(VENV) mypy $(SRC_FILES)

setup: venv-clean venv

test: venv
	$(VENV) $(TEST)

tox: venv
	TOXENV=$(TOXENV) tox

test-3.5:
	docker run --rm -it --mount type=bind,source="$(PWD)",target="/src" -w "/src" \
		python:3.5 bash -c "make clean && pip install -e .[dev] && $(TEST); make clean"

test-3.6:
	docker run --rm -it --mount type=bind,source="$(PWD)",target="/src" -w "/src" \
		python:3.6 bash -c "make clean && pip install -e .[dev] && $(TEST); make clean"

test-3.7:
	docker run --rm -it --mount type=bind,source="$(PWD)",target="/src" -w "/src" \
		python:3.7 bash -c "make clean && pip install -e .[dev] && $(TEST); make clean"

test-3.8:
	docker run --rm -it --mount type=bind,source="$(PWD)",target="/src" -w "/src" \
		python:3.8 bash -c "make clean && pip install -e .[dev] && $(TEST); make clean"

test-pypy3:
	docker run --rm -it --mount type=bind,source="$(PWD)",target="/src" -w "/src" \
		pypy:3 bash -c "make clean && pip install -e .[dev] && $(TEST); make clean"

test-all-versions: test-3.5 test-3.6 test-3.7 test-3.8 test-pypy3
