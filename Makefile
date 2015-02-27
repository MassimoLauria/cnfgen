PROJECT=cnfgen
PYTHON_BIN = /usr/bin/python
VIRTUALENV = ~/.virtualenvs/$(PROJECT)-venv


all : test



.PHONY: test install devbuild venv basic-tools editor-tools


# Build, test, install, clean
devbuild: venv
	. $(VIRTUALENV)/bin/activate
	python setup.py install

test: venv
	. $(VIRTUALENV)/bin/activate
	python setup.py test

install:
	python setup.py --user install

clean:
	rm -fr *.pyc
	rm -fr build
	rm -fr dist
	rm -fr *.egg-info


# Install basic tools for development
basic-tools:
	@type pip >/dev/null || easy_install --user pip
	@type virtualenv>/dev/null || easy_install --user virtualenv

# Install editor tools.
editor-tools : venv basic-tools
	. $(VIRTUALENV)/bin/activate
	pip install jedi
	pip install epc
	pip install pylint
	pip install nose


# Configure virtualenv
venv: $(VIRTUALENV)/bin/activate

$(VIRTUALENV)/bin/activate: requirements.txt basic-tools
	test -d $(VIRTUALENV) || virtualenv -p $(PYTHON_BIN) $(VIRTUALENV)
	. $(VIRTUALENV)/bin/activate ; pip install -Ur requirements.txt
	touch $(VIRTUALENV)/bin/activate
