PROJECT:=cnfgen
VIRTUALENV:= $(HOME)/.pyenv/versions/$(PROJECT)-venv
PYTHON=python

all : test

.PHONY: test install package upload docbuild editor-tools doc-tools venv

test: venv
	. $(VIRTUALENV)/bin/activate && \
	python setup.py nosetests --with-doctest

install:
	$(PYTHON) setup.py install --user --prefix=

clean:
	rm -fr build
	rm -fr dist
	rm -fr *.egg-info
	rm -fr docs/_build
	find . -name '*.pyc' -delete
	find . -name 'flycheck*.py' -delete

package: clean
	$(PYTHON) setup.py sdist bdist_egg bdist_wheel

upload: package
	twine upload dist/*



#
# Development is based on pyenv
#
# The environment is based on the laters 2.7 python with is neither
# a '-dev' nor an 'rc*' version. At least according to the list produced by
#
# $ pyenv install -l
#
DEV_DEPENDENCES:=pylint nose
DOC_DEPENDENCES:=sphinx sphinx-autobuild numpydoc sphinx_rtd_theme

PYENV:= $(shell command -v pyenv 2> /dev/null)
PYENV_PYVERSION:=$(shell pyenv install -l | grep '[[:space:]]2.7[[:digit:]]*[^-r]' | tail -1)

docs-build: docs-install-tools
	. $(VIRTUALENV)/bin/activate && \
	python setup.py install && \
	sphinx-apidoc -e -o docs cnfformula  && \
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
	rm -f .python-version
	pyenv virtualenv-delete -f $(PROJECT)-venv
	pyenv install -s $(PYENV_PYVERSION)
	pyenv virtualenv $(PYENV_PYVERSION) $(PROJECT)-venv
	pyenv local $(PROJECT)-venv
	. $@ && pip install -Ur requirements.txt
	. $@ && pip install $(DEV_DEPENDENCES)
	touch $@

