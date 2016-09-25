import networkx as nx

import sys
from cnfformula import CNF
from cnfformula.families.subgraph import SubgraphFormula
from cnfformula.families.subgraph import CliqueFormula
from cnfformula.families.subgraph import RamseyWitnessFormula


from cnfformula.graphs import readGraph,writeGraph
from StringIO import StringIO as sio

from . import TestCNFBase
from .test_commandline_helper import TestCommandline

from itertools import combinations

example1="""
3
1 : 2 3 0
2 : 1 0
3 : 1 0
"""

example1alt="""
3
1 : 3 0
2 : 3 0
3 : 1 2 0
"""


class TestSubgraphFormulas(TestCNFBase):
    def test_no_templates(self):
        """No templates graphs should generate an empty fomula
        """
        dimacs = """\
        p cnf 0 0
        """
        G = nx.complete_graph(4)
        F = SubgraphFormula(G,[])
        self.assertCnfEqualsDimacs(F,dimacs)


    def test_non_symmetric_input_wrong(self):
        """Symmetric encoding on non-symmetric graph

        The formula in this test uses the symmetric encoding for a non
        symmetric graph. This causes the formula to be unsatisfiable,
        even if it should be SAT.

        """
        G = readGraph(sio(example1),"simple",file_format="kthlist")
        T = readGraph(sio(example1alt),"simple",file_format="kthlist")
        F = SubgraphFormula(G,[T],symmetric=True) # This should cause the wrong answer
        self.assertUNSAT(F)

    def test_non_symmetric_input_right(self):
        """Symmetric encoding on non-symmetric graph

        The formula in this test uses the NON symmetric encoding for
        a non symmetric graph. This causes the formula to be
        satisfiable, as it should be.

        """
        G = readGraph(sio(example1),"simple",file_format="kthlist")
        T = readGraph(sio(example1alt),"simple",file_format="kthlist")
        F = SubgraphFormula(G,[T])
        self.assertSAT(F)


    def test_non_symmetric_clause_generator(self):
        """Check a tricky case in the implementation

        If the formula uses non symmetric encoding for the subset of
        vertices, then also the part of the formula about matching the
        edges requires non symmetric encoding.

        This checks that both parts are implemented correctly.
        """
        G = nx.complete_graph(4)
        T = nx.empty_graph(4)
        F = SubgraphFormula(G,[T])
        self.assertUNSAT(F)

    def test_non_symmetric_min_unsat(self):
        G = nx.complete_graph(4)
        T = nx.empty_graph(4)
        edges = list(combinations(G.nodes(),2))
        T.add_edges_from(edges[1:])
        F = SubgraphFormula(G,[T])
        self.assertUNSAT(F)
        
    def test_symmetric_min_unsat(self):
        G = nx.empty_graph(4)
        G.add_edge(0,1)
        T = nx.empty_graph(4)
        F = SubgraphFormula(G,[T])
        self.assertUNSAT(F)
        
class TestSubgraphCommandline(TestCommandline):
    def test_parameters(self):
        for base in range(2,5):
            for template in range(2,5):
                parameters = ["cnfgen","-q","subgraph",
                              "--complete", base,
                              "--completeT" , template]
                G = nx.complete_graph(base)
                T = nx.complete_graph(template)
                F = SubgraphFormula(G,[T])
                self.checkFormula(sys.stdin,F, parameters)

                parameters = ["cnfgen","-q","subgraph",
                              "--complete", base,
                              "--emptyT" , template]
                G = nx.complete_graph(base)
                T = nx.empty_graph(template)
                F = SubgraphFormula(G,[T])
                self.checkFormula(sys.stdin,F, parameters)

# class TestBinaryPigeonholePrincipleCommandline(TestCommandline):
#     def test_parameters(self):
#         for pigeons in range(2,5):
#             for holes in range(2,8):
#                 parameters = ["cnfgen","-q","bphp", pigeons, holes]
#                 F = BinaryPigeonholePrinciple(pigeons,holes)
#                 self.checkFormula(sys.stdin,F, parameters)


# class TestGraphPigeonholePrincipleCommandline(TestCommandline):
#     def test_complete(self):
#         for pigeons in range(2,5):
#             for holes in range(2,5):
#                 for functional in (True,False):
#                     for onto in (True,False):
#                         parameters = ["cnfgen","-q","gphp", "--bcomplete", pigeons, holes]
#                         if functional : parameters.append("--functional")
#                         if onto : parameters.append("--onto")
#                         graph = complete_bipartite_graph_proper(pigeons,holes)
#                         F = GraphPigeonholePrinciple(graph,functional,onto)
#                         self.checkFormula(sys.stdin,F, parameters)

#     def test_not_bipartite(self):
#         parameters = ["cnfgen","gphp", "--complete", "3"]
#         self.checkCrash(sys.stdin,parameters)
