
import sys

import networkx as nx
from networkx.algorithms.bipartite import complete_bipartite_graph

from cnfformula import CNF
from cnfformula.families.pigeonhole import PigeonholePrinciple
from cnfformula.families.pigeonhole import GraphPigeonholePrinciple
from cnfformula.families.pigeonhole import BinaryPigeonholePrinciple

from . import TestCNFBase
from .test_commandline_helper import TestCommandline

class TestPigeonholePrinciple(TestCNFBase):
    def test_empty(self):
        dimacs = """\
        p cnf 0 0
        """
        for functional in (True,False):
            for onto in (True,False):
                F = PigeonholePrinciple(0,0,functional,onto)
                self.assertCnfEqualsDimacs(F,dimacs)

    def test_one_pigeon(self):
        dimacs = """\
        p cnf 0 1
        0
        """
        for functional in (True,False):
            for onto in (True,False):
                F = PigeonholePrinciple(1,0,functional,onto)
                self.assertCnfEqualsDimacs(F,dimacs)

    def test_one_hole(self):
        dimacs = """\
        p cnf 0 0
        """
        for functional in (True,False):
                F = PigeonholePrinciple(0,1,functional,False)
                self.assertCnfEqualsDimacs(F,dimacs)

    def test_one_pigeon_one_hole(self):
        dimacs = """\
        p cnf 1 1
        1 0
        """
        for functional in (True,False):
                F = PigeonholePrinciple(1,1,functional,False)
                self.assertCnfEqualsDimacs(F,dimacs)

    def test_one_pigeon_one_hole_onto(self):
        dimacs = """\
        p cnf 1 2
        1 0
        1 0
        """
        for functional in (True,False):
                F = PigeonholePrinciple(1,1,functional,True)
                self.assertCnfEqualsDimacs(F,dimacs)

    def test_two_pigeons_three_holes(self):
        F = PigeonholePrinciple(2,3,False,False)
        dimacs = """\
        p cnf 6 5
        1 2 3 0
        4 5 6 0
        -1 -4 0
        -2 -5 0
        -3 -6 0
        """
        self.assertCnfEqualsDimacs(F,dimacs)
        
    def test_two_pigeons_two_holes_functional(self):
        F = PigeonholePrinciple(2,2,True,False)
        dimacs = """\
        p cnf 4 6
        1 2 0
        3 4 0
        -1 -3 0
        -2 -4 0
        -1 -2 0
        -3 -4 0
        """
        self.assertCnfEqualsDimacs(F,dimacs)

    def test_two_pigeons_three_holes_onto(self):
        F = PigeonholePrinciple(2,3,False,True)
        dimacs = """\
        p cnf 6 8
        1 2 3 0
        4 5 6 0
        1 4 0
        2 5 0
        3 6 0
        -1 -4 0
        -2 -5 0
        -3 -6 0
        """
        self.assertCnfEqualsDimacs(F,dimacs)

    def test_two_pigeons_two_holes_functional_onto(self):
        F = PigeonholePrinciple(2,2,True,True)
        dimacs = """\
        p cnf 4 8
        1 2 0
        3 4 0
        1 3 0
        2 4 0
        -1 -3 0
        -2 -4 0
        -1 -2 0
        -3 -4 0
        """
        self.assertCnfEqualsDimacs(F,dimacs)
        
class TestGraphPigeonholePrinciple(TestCNFBase):
    def test_empty(self):
        G = CNF()
        graph=nx.Graph()
        for functional in (True,False):
            for onto in (True,False):
                F = GraphPigeonholePrinciple(graph,functional,onto)
                self.assertCnfEqual(F,G)

    def test_complete(self):
        for pigeons in range(2,5):
            for holes in range(2,5):
                for functional in (True,False):
                    for onto in (True,False):
                        graph = complete_bipartite_graph(pigeons,holes)
                        F = GraphPigeonholePrinciple(graph,functional,onto)
                        G = PigeonholePrinciple(pigeons,holes,functional,onto)
                        self.assertCnfEquivalentModuloVariables(F,G)

    def test_not_bipartite(self):
        graph = nx.complete_graph(3)
        for functional in (True,False):
            for onto in (True,False):
                with self.assertRaises(KeyError):
                    GraphPigeonholePrinciple(graph,functional,onto)

class TestPigeonholePrincipleCommandline(TestCommandline):
    def test_parameters(self):
        for pigeons in range(2,5):
            for holes in range(2,5):
                for functional in (True,False):
                    for onto in (True,False):
                        parameters = ["cnfgen","-q","php", pigeons, holes]
                        if functional : parameters.append("--functional")
                        if onto : parameters.append("--onto")
                        F = PigeonholePrinciple(pigeons,holes,functional,onto)
                        self.checkFormula(sys.stdin,F, parameters)

class TestBinaryPigeonholePrincipleCommandline(TestCommandline):
    def test_parameters(self):
        for pigeons in range(2,5):
            for holes in range(2,8):
                parameters = ["cnfgen","-q","bphp", pigeons, holes]
                F = BinaryPigeonholePrinciple(pigeons,holes)
                self.checkFormula(sys.stdin,F, parameters)


class TestGraphPigeonholePrincipleCommandline(TestCommandline):
    def test_complete(self):
        for pigeons in range(2,5):
            for holes in range(2,5):
                for functional in (True,False):
                    for onto in (True,False):
                        parameters = ["cnfgen","-q","gphp", "--bcomplete", pigeons, holes]
                        if functional : parameters.append("--functional")
                        if onto : parameters.append("--onto")
                        graph = complete_bipartite_graph(pigeons,holes)
                        F = GraphPigeonholePrinciple(graph,functional,onto)
                        self.checkFormula(sys.stdin,F, parameters)

    def test_not_bipartite(self):
        parameters = ["cnfgen","gphp", "--complete", "3"]
        self.checkCrash(sys.stdin,parameters)
