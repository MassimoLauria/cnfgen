import sys
import unittest

from io import StringIO
from contextlib import contextmanager
from contextlib import redirect_stdout

from cnfformula import cnfgen

@contextmanager
def redirect_stderr(stream):
    """Captures stderr during a test
    TODO: move to contextlib.redirect_stderr once it is implemented
    """
    old_stderr = sys.stderr
    sys.stderr = stream
    yield
    sys.stderr = old_stderr

@contextmanager
def redirect_stdin(stream):
    """Redirect stdin during a test
    TODO: move to contextlib.redirect_stdin once it is implemented
    """
    old_stdin = sys.stdin
    sys.stdin = stream
    yield
    sys.stdin = old_stdin

    
class TestCommandline(unittest.TestCase):
    
    def checkFormula(self, indata, expected_cnf, args, cmdline=cnfgen):
        """Test that a formula generation process produces the expected formula.

        This calls a function that execute a generation process using
        the `command_line_utility` function in a module (this kind of
        functions get command line like arguments.) In particular it uses

        : cmdline.command_line_utility(args)

        to produce the formula. The generation process reads `indata`
        and produces a CNF which is supposed to be equal to `expected_cnf`.

        Parameters
        ----------
        indata : file-like
            the input data for the generation process

        expected_cnf: CNF
            a CNF that should be identical to the one produced

        args: 
            command line used to run the generation process

        cmdline: module
            reference to a module that contains `command_line_utility` method
        
        Returns
        -------
        None

        Raises
        ------
        AssertionError

        """
        parameters = [str(x) for x in args]
        f = StringIO()

        with redirect_stdout(f), redirect_stdin(indata):
            cmdline(parameters)
            
        self.assertEqual(f.getvalue(),
                         expected_cnf.dimacs(export_header=False)+'\n')

    def checkCrash(self, indata, args, cmdline=cnfgen):
        parameters = [str(x) for x in args]
        f = StringIO()
        with redirect_stdin(indata),redirect_stderr(f), self.assertRaises(SystemExit) as cm:
            cmdline(parameters)
        self.assertNotEqual(cm.exception.code, 0)
        self.assertNotEqual(f.getvalue(), '')
