import io

from cnfformula import CNF
from cnfformula import RandomKCNF
from cnfformula import Shuffle
from cnfformula import FlipPolarity

from cnfgen import cnftransform

from . import TestCNFBase
from .test_commandline_helper import TestCommandline


class TestFlip(TestCNFBase) :
    def test_double_flip(self) :
        for _ in range(10):
            cnf   = RandomKCNF(4,10,100)
            ddcnf = FlipPolarity(FlipPolarity(cnf))
            self.assertCnfEqual(cnf,ddcnf)

    def test_simple_flip(self) :
        flipped  = FlipPolarity(CNF([[(False,'x'),(False,'y'),(True,'z')]]))
        expected = CNF([[(True,'x'),(True,'y'),(False,'z')]])
        self.assertCnfEqual(expected,flipped)

    def test_polarity_shuffle_vs_flip(self) :
        cnf = CNF([[(True,'x'),(True,'y'),(False,'z')]])

        variable_permutation = list(cnf.variables())
        clause_permutation = list(range(len(cnf)))
        polarity_flip = [-1]*len(variable_permutation)
        
        shuffled = Shuffle(cnf, variable_permutation, clause_permutation, polarity_flip)
        flipped  = FlipPolarity(cnf)
        self.assertCnfEqual(flipped,shuffled)



class TestDimacsFlip(TestCommandline) :

    def test_cmdline_flip(self) :

        source   = RandomKCNF(4,10,3)
        expected = FlipPolarity(source)
        
        input_stream  = io.StringIO(source.dimacs())

        self.checkFormula(input_stream,
                          expected,
                          ['cnftransform', '-q','--input', '-', '--output', '-', 'flip'],
                          cmdline = cnftransform)
        
