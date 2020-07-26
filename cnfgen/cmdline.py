#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Components for command line interface

CNFgen has many command line entry points to its functionality, and
some of them expose the same functionality over and over. This module
contains useful common components.

Copyright (C) 2012, 2013, 2014, 2015, 2016, 2019, 2020
Massimo Lauria <massimo.lauria@uniroma1.it>
https://github.com/MassimoLauria/cnfgen.git

"""

import os
import sys
import argparse
import subprocess
import tempfile
import signal

from contextlib import redirect_stdout
from contextlib import contextmanager


@contextmanager
def paginate_or_redirect_stdout(outputstream):
    """Output to a file or, when interactive, to the PAGER

    Redirect standard output to ``outputstream``. Furthermore when the
    standard output is supposed to go to an interactive terminal (i.e.
    it has not been piped to a file or to another process) then
    instead of flashing it on the screen this context manager
    redirects it to a temporary file which is shown by `$PAGER`, or by
    `less` if PAGER environment variable is not defined.
    """

    with redirect_stdout(outputstream):
        use_pager = sys.stdout.isatty()
        pager = os.getenv('PAGER', 'less')

        if use_pager:
            path = tempfile.mkstemp()[1]
            tmp_file = open(path, 'a')
        else:
            tmp_file = sys.stdout

        with redirect_stdout(tmp_file):
            yield

        if use_pager:
            tmp_file.flush()
            tmp_file.close()
            p = subprocess.Popen([pager, path], stdin=subprocess.PIPE)
            p.communicate()


@contextmanager
def redirect_stdin(stream):
    """Redirect stdin during a test
    TODO: move to contextlib.redirect_stdin once it is implemented
    """
    old_stdin = sys.stdin
    sys.stdin = stream
    yield
    sys.stdin = old_stdin


def setup_SIGINT():
    """Register a handler for SIGINT signal

    Register a handler that manages keyboard interruptions
    via SIGINT.
    """
    def sigint_handler(insignal, frame):

        progname = os.path.basename(sys.argv[0])
        signame = signal.Signals(insignal).name
        print('{} received: program \'{}\' stops.'.format(signame, progname),
              file=sys.stderr)
        sys.exit(-1)

    signal.signal(signal.SIGINT, sigint_handler)


def find_in_package(package, test, sortkey=None):
    """Explore a package for items that satisfy a speficic test"""
    import pkgutil

    result = []

    if sortkey is None:
        sortkey = str

    for loader, module_name, _ in pkgutil.walk_packages(package.__path__):
        module_name = package.__name__ + "." + module_name
        if module_name in sys.modules:
            module = sys.modules[module_name]
        else:
            module = loader.find_module(module_name).load_module(module_name)
        for objname in dir(module):
            obj = getattr(module, objname)
            if test(obj):
                result.append(obj)
    result.sort(key=sortkey)
    return result


def get_transformation_helpers():

    import cnfgen
    from .transformation_helpers import TransformationHelper

    def test(x):
        return isinstance(x, type) and \
            issubclass(x, TransformationHelper) and \
            x != TransformationHelper

    return find_in_package(cnfgen, test, sortkey=lambda x: x.name)


def get_formula_helpers():

    import cnfgen
    from .formula_helpers import FormulaHelper

    def test(x):
        return isinstance(x, type) and \
            issubclass(x, FormulaHelper) and \
            x != FormulaHelper

    return find_in_package(cnfgen, test, sortkey=lambda x: x.name)


class CLIError(Exception):
    """Error related to the command line arguments

This error occurs when the command line contains some errors. """
    pass


class CLIParser(argparse.ArgumentParser):
    """Argument Parser for CNFGen

Exactly as argparse.ArgumentParser, but the error function raises an
exception, instead of calling exit.
"""
    def __init(self,
               prog=None,
               usage=None,
               description=None,
               epilog=None,
               parents=[],
               prefix_chars='-',
               fromfile_prefix_chars=None,
               argument_default=None,
               formatter_class=argparse.RawDescriptionHelpFormatter,
               conflict_handler='error',
               add_help=True,
               allow_abbrev=True):
        super(CLIParser,
              self).__init__(prog=prog,
                             usage=usage,
                             description=description,
                             epilog=epilog,
                             parents=parents,
                             formatter_class=formatter_class,
                             prefix_chars=prefix_chars,
                             fromfile_prefix_chars=fromfile_prefix_chars,
                             argument_default=argument_default,
                             conflict_handler=conflict_handler,
                             add_help=add_help,
                             allow_abbrev=allow_abbrev)

    def error(self, message):
        message = str(message)
        errstr = ["ERROR: " + x for x in message.splitlines()]
        errstr.append("")

        if self.usage is not None:
            errstr.append(self.usage)
            errstr.append("")

        if self.description is not None:
            errstr.append(self.description)
            errstr.append("")

        errstr.append("See '{0} -h' or '{0} --help' for more info.".format(
            self.prog))

        raise CLIError("\n".join(errstr))


def positive_int(value):
    errmsg = "{} was supposed to be a positive integer".format(value)
    try:
        ivalue = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(errmsg)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(errmsg)
    return ivalue


def nonnegative_int(value):
    errmsg = "{} was supposed to be a non negative integer".format(value)
    try:
        ivalue = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(errmsg)
    if ivalue < 0:
        raise argparse.ArgumentTypeError(errmsg)
    return ivalue


def probability(value):
    errmsg = "{} was supposed to be a real number in [0,1]".format(value)
    try:
        p = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(errmsg)
    if not (0 <= p <= 1.0):
        raise argparse.ArgumentTypeError(errmsg)
    return p
