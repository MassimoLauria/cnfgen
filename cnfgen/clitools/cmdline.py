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

from cnfgen.clitools.graph_args import ObtainGraphAction


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

    import cnfgen.clihelpers
    from cnfgen.clihelpers.transformation_helpers import TransformationHelper

    def test(x):
        return isinstance(x, type) and \
            issubclass(x, TransformationHelper) and \
            x != TransformationHelper

    return find_in_package(cnfgen.clihelpers, test, sortkey=lambda x: x.name)


def get_formula_helpers():

    import cnfgen.clihelpers
    from cnfgen.clihelpers.formula_helpers import FormulaHelper

    def test(x):
        return isinstance(x, type) and \
            issubclass(x, FormulaHelper) and \
            x != FormulaHelper

    return find_in_package(cnfgen.clihelpers, test, sortkey=lambda x: x.name)


class CLIError(Exception):
    """Error related to the command line arguments

This error occurs when the command line contains some errors. """
    pass


class CLIHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def _format_args(self, action, default_metavar):
        get_metavar = self._metavar_formatter(action, default_metavar)
        if isinstance(action, ObtainGraphAction):
            result = '%s' % get_metavar(1)
            return result
        else:
            return super(CLIHelpFormatter,
                         self)._format_args(action, default_metavar)


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
               conflict_handler='error',
               add_help=True,
               allow_abbrev=True):
        super(CLIParser,
              self).__init__(prog=prog,
                             usage=usage,
                             description=description,
                             epilog=epilog,
                             parents=parents,
                             formatter_class=CLIHelpFormatter,
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


def positive_even_int(value):
    errmsg = "{} was supposed to be an even integer".format(value)
    ivalue = positive_int(value)
    if ivalue % 2 != 0:
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


def compose_two_parsers(parser1, parser2, test=None):
    """Create an argparse action which compose two parsers

The action takes all remaining arguments and uses a test to determine
which parser should parse them, using `test` function, given as argument.

If `test` is `None` then uses the default test:
     is the first argument a number ---> parser1
     otherwise ---> parser2
"""
    class TmpAction(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):

            nonlocal test

            parser1.prog = parser.prog
            parser2.prog = parser.prog

            if len(values) == 0:
                parser.error("{0} requires some arguments.".format(
                    parser.prog))

            def is_first_a_number(x):
                try:
                    float(x[0])
                    return True
                except ValueError:
                    return False

            if test is None:
                test = is_first_a_number

            if test(values):
                parser1.parse_args(values, namespace=args)
            else:
                parser2.parse_args(values, namespace=args)

    return TmpAction
