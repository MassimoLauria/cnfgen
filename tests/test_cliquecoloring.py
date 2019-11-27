import sys

from cnfformula import CNF
from cnfformula import CliqueColoring

from . import TestCNFBase
from .test_commandline_helper import TestCommandline

class TestCliqueColoring(TestCNFBase):

    def test_5wheel(self):
        F = CliqueColoring(6,3,4)
        self.assertSAT(F)

    def test_unsat(self):
        F = CliqueColoring(6,4,3)
        self.assertUNSAT(F)

class TestCliqueColoringCnfgen(TestCommandline):
    def test_k4_c3(self):
        for n in range(4,6):
            parameters = ["cnfgen","-q","cliquecoloring", n, 4, 3]
            F = CliqueColoring(n, 4, 3)
            self.checkFormula(sys.stdin, F, parameters)

    def test_k3_c4(self):
        for n in range(4,6):
            parameters = ["cnfgen","-q","cliquecoloring", n, 3, 4]
            F = CliqueColoring(n, 3, 4)
            self.checkFormula(sys.stdin, F, parameters)
