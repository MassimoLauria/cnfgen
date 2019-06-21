import sys


import cnfformula

from cnfformula.utils.kthlist2pebbling import command_line_utility as kthlist2pebbling
from .test_commandline_helper import TestCommandline

from cnfformula.graphs import readGraph
from cnfformula.families.pebbling import PebblingFormula

from cnfformula.transformations.substitutions import BaseSubstitution
from cnfformula.transformations.substitutions import OrSubstitution
from cnfformula.transformations.substitutions import XorSubstitution
from cnfformula.transformations.substitutions import FormulaLifting

import io

class TestKTHList2Pebbling(TestCommandline) :

    def test_unit_graph(self) :

        input = io.StringIO("1\n1 : 0\n")
        F = PebblingFormula(readGraph(input,'dag','kthlist'))

        input.seek(0)
        self.checkFormula(input,F,["kthlist2pebbling","-q","none"],cmdline = kthlist2pebbling)

    def test_small_line(self) :

        input = io.StringIO("3\n1 : 0\n2 : 1 0\n3 : 2 0\n")
        F = PebblingFormula(readGraph(input,'dag','kthlist'))

        input.seek(0)
        self.checkFormula(input,F,["kthlist2pebbling","-q","none"],cmdline = kthlist2pebbling)

    def test_small_pyramid(self) :
        input = io.StringIO("3\n1 : 0\n2 : 0\n3 : 1 2 0\n")
        F = PebblingFormula(readGraph(input,'dag','kthlist'))
        input.seek(0)
        self.checkFormula(input,F,["kthlist2pebbling","-q","none"],cmdline = kthlist2pebbling)
        
    def test_or_substitution(self) :
        input = io.StringIO("3\n1 : 0\n2 : 0\n3 : 1 2 0\n")
        G = PebblingFormula(readGraph(input,'dag','kthlist'))
        F = OrSubstitution(G,2)
        input.seek(0)
        self.checkFormula(input,F,["kthlist2pebbling","-q","or",2],cmdline = kthlist2pebbling)

    def test_lift_substitution(self) :
        input = io.StringIO("3\n1 : 0\n2 : 0\n3 : 1 2 0\n")
        G = PebblingFormula(readGraph(input,'dag','kthlist'))
        F = FormulaLifting(G,3)
        input.seek(0)
        self.checkFormula(input,F,["kthlist2pebbling","-q","lift",3],cmdline = kthlist2pebbling)
    
    def test_xor_substitution(self) :
        input = io.StringIO("3\n1 : 0\n2 : 0\n3 : 1 2 0\n")
        G = PebblingFormula(readGraph(input,'dag','kthlist'))
        F = XorSubstitution(G,2)
        input.seek(0)
        self.checkFormula(input,F,["kthlist2pebbling","-q","xor",2],cmdline = kthlist2pebbling)
