#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Components for command line interface

CNFgen has many command line entry points to its functionality, and
some of them expose the same functionality over and over. This module
contains useful common components. 

Copyright (C) 2012, 2013, 2014, 2015, 2016, 2019  Massimo Lauria <massimo.lauria@uniroma1.it>
https://github.com/MassimoLauria/cnfgen.git

"""



import os
import sys
import argparse
import subprocess
import tempfile
import signal
import textwrap

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

            
def interactive_msg(msg, prefix='', filltext=70):
    """Writes a message to the interactive user (if present).

    When the input comes from an interactive user on the terminal, it
    is useful to give them feedback regarding the expected output.
    This message is sent to stderr in order to help interactive usage,
    but it is not sent out if input comes from a non interactive
    terminal.
    """
    msg = textwrap.dedent(msg)
    if filltext is not None and filltext>0:
        msg = textwrap.fill(msg, width=filltext-len(prefix))
    msg = textwrap.indent(msg, prefix, lambda line: True)

    if sys.stdin.isatty():
        print(msg, file = sys.stderr)

def error_msg(msg, prefix='', filltext=70):
    """Writes an error message.

    """
    msg = textwrap.dedent(msg)
    if filltext is not None and filltext>0:
        msg = textwrap.fill(msg, width=filltext-len(prefix))
    msg = textwrap.indent(msg, prefix, lambda line: True)
    print(msg, file=sys.stderr)


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


    
        
