PROJECT=cnfgen
PYTHON_BIN = /usr/bin/python
VIRTUALENV = $(HOME)/.virtualenvs/$(PROJECT)-venv


all : test



.PHONY: test install devbuild venv editor-tools doc-tools docs


# Build, test, install, clean
devbuild: venv
	. $(VIRTUALENV)/bin/activate && \
	python setup.py install

test: venv
	. $(VIRTUALENV)/bin/activate && \
	python setup.py nosetests --with-doctest

install:
	python setup.py install --user

clean:
	rm -fr *.pyc
	rm -fr build
	rm -fr dist
	rm -fr *.egg-info
	rm -fr docs/_build

docs: devbuild
	. $(VIRTUALENV)/bin/activate && \
	sphinx-apidoc -o docs cnfformula && \
	$(MAKE) -C docs html

# Install editor tools.
editor-tools : venv
	. $(VIRTUALENV)/bin/activate && \
	pip install jedi epc pylint nose six service_factory

# Install documentation tools.
doc-tools : venv
	. $(VIRTUALENV)/bin/activate && \
	pip install sphinx sphinx-autobuild numpydoc sphinx_rtd_theme


# Configure virtualenv
venv: $(VIRTUALENV)/bin/activate

$(VIRTUALENV)/bin/activate: requirements.txt
	type pip >/dev/null || easy_install --user pip
	type virtualenv>/dev/null || easy_install --user virtualenv
	test -d $(VIRTUALENV) || virtualenv -p $(PYTHON_BIN) $(VIRTUALENV)
	. $@ && pip install -Ur requirements.txt
	touch $@

