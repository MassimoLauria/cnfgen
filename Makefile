PROJECT:=cnfgen
VERSIONFILE=$(PROJECT)/version.py

VIRTUALENV:= $(PWD)/.venv/$(PROJECT)-venv
ACTIVATE:= $(VIRTUALENV)/bin/activate

DEV_DEPENDENCES:=yapf pytest pytest-datadir flake8
PKG_DEPENDENCES:=setuptools wheel twine keyring build
DOC_DEPENDENCES:=sphinx sphinx-autobuild numpydoc sphinx_rtd_theme sphinx-autodoc-typehints docutils intersphinx_registry

all : test

.PHONY: test install clean venv
.PHONY: docs docs-install-tools
.PHONY: package upload

$(VERSIONFILE):
	echo "version = '"`git describe --always --tags | sed s/-g/+g/g`"'" > $(VERSIONFILE)

test: $(VERSIONFILE) $(ACTIVATE)
	. $(ACTIVATE) && pytest

clean:
	rm -fr version.py
	rm -fr build
	rm -fr dist
	rm -fr *.egg-info
	rm -fr docs/_build
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	find . -name 'flycheck*.py' -delete

package: $(VERSIONFILE) $(ACTIVATE)
	$(MAKE) clean
	. $(ACTIVATE) && python -m build

upload: package
	twine upload --repository cnfgen dist/*


docs: $(VERSIONFILE)
	. $(ACTIVATE) && pip install -U $(DOC_DEPENDENCES)
	. $(ACTIVATE) && \
	pip install -e . && \
	sphinx-apidoc -e -o docs $(PROJECT)  && \
	$(MAKE) -C docs html && \
	pip uninstall -y $(PROJECT)

docs-install-tools :  $(ACTIVATE)
	. $(ACTIVATE) && pip install -U $(DOC_DEPENDENCES)


venv: $(ACTIVATE)

$(VIRTUALENV)/bin/activate: requirements.txt
	@echo "Setting up virtualenv $(PROJECT) in $(VIRTUALENV)"
	python -m venv --clear --upgrade-deps $(VIRTUALENV)
	. $@ && pip install -U pip
	. $@ && pip install -Ur requirements.txt
	. $@ && pip install $(DEV_DEPENDENCES)
	. $@ && pip install $(PKG_DEPENDENCES)
	. $@ && pip install -e .
	touch $@
