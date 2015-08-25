import cnfformula.utils.adjlist2pebbling as adjlist2pebbling

from . import TestCNFBase

import cnfformula
import cnfformula.cnfgen as cnfgen
from cnfformula.graphs import readGraph
from cnfformula import PebblingFormula

import StringIO

class TestAdjList2Pebbling(TestCNFBase) :
    def identity_check_helper(self, input, liftname, liftrank) :
        G = readGraph(input,'dag','adjlist')
        input.seek(0)
        peb = PebblingFormula(G)
        lift = cnfformula.TransformFormula(peb, liftname, liftrank)
        reference_output = lift.dimacs(export_header=False)+"\n"
        
        tool_output=StringIO.StringIO()
        adjlist2pebbling.adjlist2pebbling(input, liftname, liftrank, tool_output, header=True)
        self.assertMultiLineEqual(tool_output.getvalue(), reference_output)

    def test_unit_graph(self) :
        input = StringIO.StringIO("1\n1 :\n")
        self.identity_check_helper(input, 'none', 0)

    def test_small_line(self) :
        input = StringIO.StringIO("3\n1 :\n2 : 1\n3 : 2\n")
        self.identity_check_helper(input, 'none', 0)

    def test_small_pyramid(self) :
        input = StringIO.StringIO("3\n1 : \n2 : \n3 : 1 2\n")
        self.identity_check_helper(input, 'none', 0)        
        
    def test_substitution(self) :
        input = StringIO.StringIO("3\n1 : \n2 : \n3 : 1 2\n")
        self.identity_check_helper(input, 'or', 2)
