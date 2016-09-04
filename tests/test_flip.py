import cnfformula.utils.cnfshuffle as cnfshuffle

from . import TestCNFBase
from test_cnfformula import TestCNF
from cnfformula import FlipPolarity,Shuffle,cnfgen,CNF

from cnfformula.utils.dimacstransform import command_line_utility as dimacstransform

import random
import StringIO

class TestFlip(TestCNF) :
    def test_double_flip(self) :
        for _ in range(10):
            cnf   = self.random_cnf(4,10,100)
            ddcnf = FlipPolarity(FlipPolarity(cnf))
            self.assertCnfEqual(cnf,ddcnf)

    def test_simple_flip(self) :
        flipped  = FlipPolarity(CNF([[(False,'x'),(False,'y'),(True,'z')]]))
        expected = CNF([[(True,'x'),(True,'y'),(False,'z')]])
        self.assertCnfEqual(expected,flipped)

    def test_polarity_shuffle_vs_flip(self) :
        cnf = CNF([[(True,'x'),(True,'y'),(False,'z')]])

        variable_permutation = list(cnf.variables())
        clause_permutation = range(len(cnf))
        polarity_flip = [-1]*len(variable_permutation)
        
        shuffled = Shuffle(cnf, variable_permutation, clause_permutation, polarity_flip)
        flipped  = FlipPolarity(cnf)
        self.assertCnfEqual(flipped,shuffled)



class TestDimacsFlip(TestCNF) :

    def test_cmdline_flip(self) :

        cnf = self.random_cnf(4,10,3)
        shuffle = FlipPolarity(cnf)
        
        reference_output = shuffle.dimacs(export_header=False) + '\n'

        input_stream = StringIO.StringIO(cnf.dimacs())
        dimacs_flip = StringIO.StringIO()

        argv=['dimacstransform', '-q','--input', '-', '--output', '-', 'flip']
        try:
            import sys
            sys.stdin = input_stream
            sys.stdout = dimacs_flip
            dimacstransform(argv)
        except Exception as e:
            self.fail(e)
        finally:
            sys.stdin = sys.__stdin__
            sys.stdout = sys.__stdout__
        self.assertMultiLineEqual(dimacs_flip.getvalue(), reference_output)
