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

class TestCommandline(unittest.TestCase):
    def checkFormula(self, cnf, parameters):
        parameters = ["cnfgen"] + parameters
        parameters = [unicode(x) for x in parameters]
        print(parameters)
        f = StringIO()
        with stdout_redirector(f):
            cnfgen.command_line_utility(parameters)
        self.assertEqual(f.getvalue(),cnf.dimacs()+'\n')
