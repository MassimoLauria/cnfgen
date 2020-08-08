#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Screen messages for CNFgen interaction
"""

import sys
import textwrap
from contextlib import contextmanager

_prefix = ''


@contextmanager
def msg_prefix(new_prefix=''):
    """Set prefix for all interactive messages"""
    global _prefix
    old_prefix = _prefix
    _prefix = old_prefix + new_prefix
    yield
    _prefix = old_prefix


def interactive_msg(msg, filltext=None):
    """Writes a message to the interactive user (if present).

    When the input comes from an interactive user on the terminal, it
    is useful to give them feedback regarding the expected output.
    This message is sent to stderr in order to help interactive usage,
    but it is not sent out if input comes from a non interactive
    terminal.
    """
    global _prefix
    msg = textwrap.dedent(msg)
    if filltext is not None and filltext > len(_prefix) + 30:
        msg = textwrap.fill(msg, width=filltext - len(_prefix))
    msg = textwrap.indent(msg, _prefix, lambda line: True)

    if sys.stdin.isatty():
        print(msg, file=sys.stderr)


def error_msg(msg, filltext=None):
    """Writes an error message.

    """
    global _prefix
    msg = textwrap.dedent(str(msg))
    if filltext is not None and filltext > 0:
        msg = textwrap.fill(msg, width=filltext - len(_prefix))
    msg = textwrap.indent(msg, _prefix, lambda line: True)
    print(msg, file=sys.stderr)


class InternalBug(Exception):
    """Bug related to internal consistency
    """
    def __init__(self, msg):

        bug_msg = """INTERNAL ERROR

{}

Ooops! This was never supposed to happen. Please
take note of your command line and send it to
<massimo.lauria@uniroma1.it>
""".format(str(msg))
        super(Exception, self).__init__(bug_msg)
