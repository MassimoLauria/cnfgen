import sys
import pytest

from cnfgen import CNF
from cnfgen import PigeonholePrinciple
from cnfgen import GraphPigeonholePrinciple
from cnfgen import BinaryPigeonholePrinciple
from cnfgen.graphs import BipartiteGraph, CompleteBipartiteGraph

import networkx as nx

from cnfgen.clitools import cnfgen, CLIError

from tests.utils import assertUNSAT, assertCnfEqual, assertCnfEqualsDimacs, assertCnfEqualsIgnoreVariables


def test_empty():
    dimacs = """\
    p cnf 0 0
    """
    for functional in (True, False):
        for onto in (True, False):
            F = PigeonholePrinciple(0, 0, functional, onto)
            assertCnfEqualsDimacs(F, dimacs)


def test_one_pigeon():
    dimacs = """\
    p cnf 0 1
    0
    """
    for functional in (True, False):
        for onto in (True, False):
            F = PigeonholePrinciple(1, 0, functional, onto)
            assertCnfEqualsDimacs(F, dimacs)


def test_one_hole():
    dimacs = """\
    p cnf 0 0
    """
    for functional in (True, False):
        F = PigeonholePrinciple(0, 1, functional, False)
        assertCnfEqualsDimacs(F, dimacs)


def test_one_pigeon_one_hole():
    dimacs = """\
    p cnf 1 1
    1 0
    """
    for functional in (True, False):
        F = PigeonholePrinciple(1, 1, functional, False)
        assertCnfEqualsDimacs(F, dimacs)


def test_one_pigeon_one_hole_onto():
    dimacs = """\
    p cnf 1 2
    1 0
    1 0
    """
    for functional in (True, False):
        F = PigeonholePrinciple(1, 1, functional, True)
        assertCnfEqualsDimacs(F, dimacs)


def test_two_pigeons_three_holes():
    F = PigeonholePrinciple(2, 3, False, False)
    dimacs = """\
    p cnf 6 5
    1 2 3 0
    4 5 6 0
    -1 -4 0
    -2 -5 0
    -3 -6 0
    """
    assertCnfEqualsDimacs(F, dimacs)


def test_two_pigeons_two_holes_functional():
    F = PigeonholePrinciple(2, 2, True, False)
    dimacs = """\
    p cnf 4 6
    1 2 0
    3 4 0
    -1 -3 0
    -2 -4 0
    -1 -2 0
    -3 -4 0
    """
    assertCnfEqualsDimacs(F, dimacs)


def test_two_pigeons_three_holes_onto():
    F = PigeonholePrinciple(2, 3, False, True)
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
    assertCnfEqualsDimacs(F, dimacs)


def test_two_pigeons_two_holes_functional_onto():
    F = PigeonholePrinciple(2, 2, True, True)
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
    assertCnfEqualsDimacs(F, dimacs)


def test_empty_graph():
    G = CNF()
    graph = BipartiteGraph(0, 0)
    for functional in (True, False):
        for onto in (True, False):
            F = GraphPigeonholePrinciple(graph, functional, onto)
            assertCnfEqual(F, G)


def test_complete():
    for pigeons in range(2, 5):
        for holes in range(2, 5):
            for functional in (True, False):
                for onto in (True, False):
                    graph = CompleteBipartiteGraph(pigeons, holes)
                    F = GraphPigeonholePrinciple(graph, functional, onto)
                    G = PigeonholePrinciple(pigeons, holes, functional, onto)
                    assertCnfEqualsIgnoreVariables(F, G)


def test_gphp_not_bipartite():
    graph = nx.complete_graph(3)
    for functional in (True, False):
        for onto in (True, False):
            with pytest.raises(ValueError):
                GraphPigeonholePrinciple(graph, functional, onto)


def test_php_lib_vs_cli():
    """PHP comparison between command line and library

To avoid mismatches in the header, we compare the dimacs output
without the comments.
"""
    for functional in (True, False):
        for onto in (True, False):
            parameters = ["cnfgen", "-q", "php", "5", "4"]
            if functional:
                parameters.append("--functional")
            if onto:
                parameters.append("--onto")
            F = PigeonholePrinciple(5, 4, functional, onto)
            lib = F.dimacs(export_header=False)
            cli = cnfgen(parameters, mode='string')
            assert lib == cli


def test_php_cli_wrong():
    """PHP command line must not accept wrong args"""
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", "php", "aaad", "sdda"])


def test_php_cli_negative():
    """PHP command line must not accept negative args"""
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", "php", "-3", "1"])


def test_php_lib_params():
    """ValueError for invalid number of pigeons/holes

"""
    with pytest.raises(ValueError):
        PigeonholePrinciple(-3, 3)

    with pytest.raises(ValueError):
        PigeonholePrinciple(3, -3)


# Binary PHP
def test_bphp_lib_vs_cli():
    F = BinaryPigeonholePrinciple(5, 8)
    lib = F.dimacs(export_header=False)
    cli = cnfgen(["cnfgen", "-q", "bphp", '5', '8'], mode='string')
    assert lib == cli


def test_bphp_example():

    F = BinaryPigeonholePrinciple(4, 2)
    assert len(list(F.variables())) == 4
    assert len(list(F.clauses())) == 12
    for c in F.clauses():
        assert len(c) == 2


def test_bphp_unsat():
    F = BinaryPigeonholePrinciple(4, 2)
    assertUNSAT(F)


def test_gphp_lib_vs_cli():
    for functional in (True, False):
        for onto in (True, False):
            parameters = ["cnfgen", "-q", "php", "complete", '5', '4']
            if functional:
                parameters.append("--functional")
            if onto:
                parameters.append("--onto")
            graph = CompleteBipartiteGraph(5, 4)
            F = GraphPigeonholePrinciple(graph, functional, onto)
            lib = F.to_dimacs()
            cli = cnfgen(parameters, mode='string')
            assert cli == lib


def test_not_bipartite():
    with pytest.raises(CLIError):
        cnfgen(["cnfgen", "php", "complete", "3"])
