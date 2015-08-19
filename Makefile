PROJECT=cnfgen
PYTHON_BIN = /usr/bin/python
VIRTUALENV = $(HOME)/.virtualenvs/$(PROJECT)-venv

all : test

.PHONY: test install package dist devbuild docbuild editor-tools doc-tools venv

test: venv
	. $(VIRTUALENV)/bin/activate && \
	python setup.py nosetests --with-doctest

install:
	python setup.py install --user --prefix=

clean:
	rm -fr build
	rm -fr dist
	rm -fr *.egg-info
	rm -fr docs/_build
	find . -name '*.pyc' -delete
	find . -name 'flycheck*.py' -delete

package: clean
	python setup.py sdist bdist_wheel

dist: package
	twine upload dist/*



#
# Develop
# 
devbuild: venv
	. $(VIRTUALENV)/bin/activate && \
	python setup.py install

docbuild: devbuild
	. $(VIRTUALENV)/bin/activate && \
	sphinx-apidoc -o docs cnfformula && \
	$(MAKE) -C docs html

#
# Install tools
#
editor-tools : venv
	. $(VIRTUALENV)/bin/activate && \
	pip install jedi epc pylint nose six service_factory

doc-tools : venv
	. $(VIRTUALENV)/bin/activate && \
	pip install sphinx sphinx-autobuild numpydoc sphinx_rtd_theme


#
# virtualenv setup
#
venv: $(VIRTUALENV)/bin/activate

$(VIRTUALENV)/bin/activate: requirements.txt
	type pip >/dev/null || easy_install --user pip
	type virtualenv>/dev/null || easy_install --user virtualenv
	test -d $(VIRTUALENV) || virtualenv -p $(PYTHON_BIN) $(VIRTUALENV)
	. $@ && pip install -Ur requirements.txt
	touch $@

