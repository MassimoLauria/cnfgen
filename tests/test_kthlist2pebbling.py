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

import StringIO

class TestKTHList2Pebbling(TestCommandline) :

    def test_unit_graph(self) :

        input = StringIO.StringIO("1\n1 :\n")
        F = PebblingFormula(readGraph(input,'dag','kthlist'))

        input.seek(0)
        self.checkFormula(input,F,["kthlist2pebbling","none"],cmdline = kthlist2pebbling)

    def test_small_line(self) :

        input = StringIO.StringIO("3\n1 :\n2 : 1\n3 : 2\n")
        F = PebblingFormula(readGraph(input,'dag','kthlist'))

        input.seek(0)
        self.checkFormula(input,F,["kthlist2pebbling","none"],cmdline = kthlist2pebbling)

    def test_small_pyramid(self) :
        input = StringIO.StringIO("3\n1 : \n2 : \n3 : 1 2\n")
        F = PebblingFormula(readGraph(input,'dag','kthlist'))
        input.seek(0)
        self.checkFormula(input,F,["kthlist2pebbling","none"],cmdline = kthlist2pebbling)
        
    def test_or_substitution(self) :
        input = StringIO.StringIO("3\n1 : \n2 : \n3 : 1 2\n")
        G = PebblingFormula(readGraph(input,'dag','kthlist'))
        F = OrSubstitution(G,2)
        input.seek(0)
        self.checkFormula(input,F,["kthlist2pebbling","or",2],cmdline = kthlist2pebbling)

    def test_lift_substitution(self) :
        input = StringIO.StringIO("3\n1 : \n2 : \n3 : 1 2\n")
        G = PebblingFormula(readGraph(input,'dag','kthlist'))
        F = FormulaLifting(G,3)
        input.seek(0)
        self.checkFormula(input,F,["kthlist2pebbling","lift",3],cmdline = kthlist2pebbling)
    
    def test_xor_substitution(self) :
        input = StringIO.StringIO("3\n1 : \n2 : \n3 : 1 2\n")
        G = PebblingFormula(readGraph(input,'dag','kthlist'))
        F = XorSubstitution(G,2)
        input.seek(0)
        self.checkFormula(input,F,["kthlist2pebbling","xor",2],cmdline = kthlist2pebbling)
