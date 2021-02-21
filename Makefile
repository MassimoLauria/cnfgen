PROJECT:=cnfgen
VIRTUALENV:= $(HOME)/.pyenv/versions/$(PROJECT)-venv
PYTHON=python
VERSIONFILE=$(PROJECT)/version.py

all : test

.PHONY: test install clean venv force
.PHONY: docs docs-install-tools
.PHONY: testpackage package upload

$(VERSIONFILE): force
	@echo "version = '"`git describe --always --tags`"'" > $(VERSIONFILE)

test: venv $(VERSIONFILE)
	. $(VIRTUALENV)/bin/activate && \
	pytest

install: $(VERSIONFILE)
	$(PYTHON) setup.py install --user

clean:
	rm -fr version.py
	rm -fr build
	rm -fr dist
	rm -fr *.egg-info
	rm -fr docs/_build
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	find . -name 'flycheck*.py' -delete

package:
	$(MAKE) clean
	$(MAKE) $(VERSIONFILE)
	$(PYTHON) setup.py sdist bdist_egg bdist_wheel


testpackage: test
	$(MAKE) clean
	$(MAKE) $(VERSIONFILE)
	$(eval pkgname=$(shell $(PYTHON) setup.py --name)-$(shell $(PYTHON) setup.py --version))
	$(PYTHON) setup.py sdist
	cd dist && \
	tar xfz $(pkgname).tar.gz && \
	cd $(pkgname) && \
	$(PYTHON) setup.py build
	rm -fr dist/$(pkgname)

upload: testpackage
	$(MAKE) package
	twine upload dist/*

#
# Development is based on pyenv
#
# The environment is based on the latest 3.8 python with is neither
# a '-dev' nor an 'rc*' version. At least according to the list produced by
#
# $ pyenv install -l
#
DEV_DEPENDENCES:=yapf pytest pytest-datadir flake8 'python-language-server[all]'
PKG_DEPENDENCES:=wheel twine keyring
DOC_DEPENDENCES:=sphinx sphinx-autobuild numpydoc sphinx_rtd_theme

PYENV:= $(shell command -v pyenv 2> /dev/null)
PYENV_PYVERSION:=$(shell pyenv install -l | grep '[[:space:]]3.9.[[:digit:]]*' | grep -v 'rc\|dev' | tail -1)

docs: docs-install-tools $(VERSIONFILE)
	. $(VIRTUALENV)/bin/activate && \
	python setup.py install && \
	sphinx-apidoc -e -o docs $(PROJECT)  && \
	$(MAKE) -C docs html && \
	pip uninstall -y $(PROJECT)

docs-install-tools : venv
	. $(VIRTUALENV)/bin/activate && \
	pip install $(DOC_DEPENDENCES)


venv: $(VIRTUALENV)/bin/activate

$(VIRTUALENV)/bin/activate: requirements.txt
ifndef PYENV
    $(error "Development is based on pyenv, please install it.")
endif
	@echo "Setting up virtualenv $(PROJECT) using python $(PYENV_PYVERSION)"
	-rm -f .python-version
	-pyenv virtualenv-delete -f $(PROJECT)-venv
	pyenv install -s $(PYENV_PYVERSION)
	pyenv virtualenv $(PYENV_PYVERSION) $(PROJECT)-venv
	pyenv local $(PROJECT)-venv
	. $@ && pip install -U pip
	. $@ && pip install -Ur requirements.txt
	. $@ && pip install $(DEV_DEPENDENCES)
	. $@ && pip install $(PKG_DEPENDENCES)
	. $@ && pip install -e .
	touch $@
