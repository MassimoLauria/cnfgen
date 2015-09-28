import unittest
from contextlib import contextmanager
from cStringIO import StringIO
import sys

import cnfformula.cnfgen as cnfgen

@contextmanager
def stdout_redirector(stream):
    """Captures stdout during a test
    TODO: move to contextlib.redirect_stdout once we can use Python 3
    http://eli.thegreenplace.net/2015/redirecting-all-kinds-of-stdout-in-python/
    """
    old_stdout = sys.stdout
    sys.stdout = stream
    yield
    sys.stdout = old_stdout

@contextmanager
def stderr_redirector(stream):
    """Captures stderr during a test
    TODO: move to contextlib.redirect_stderr once we can use Python 3
    """
    old_stderr = sys.stderr
    sys.stderr = stream
    yield
    sys.stderr = old_stderr

class TestCommandline(unittest.TestCase):
    def checkFormula(self, cnf, parameters):
        parameters = ["cnfgen"] + parameters
        parameters = [str(x) for x in parameters]
        f = StringIO()
        with stdout_redirector(f):
            cnfgen.command_line_utility(parameters)
        self.assertEqual(f.getvalue(),cnf.dimacs()+'\n')

    def checkCrash(self, parameters):
        parameters = ["cnfgen"] + parameters
        parameters = [str(x) for x in parameters]
        f = StringIO()
        with stderr_redirector(f), self.assertRaises(SystemExit) as cm:
            cnfgen.command_line_utility(parameters)
        self.assertNotEqual(cm.exception.code, 0)
        self.assertNotEqual(f.getvalue(),'')
