import pytest
import networkx as nx
import sys

from cnfformula import CNF
from cnfformula import OrderingPrinciple, GraphOrderingPrinciple
from cnfgen.clitools import cnfgen, CLIError
from tests.utils import assertCnfEqual, assertCnfEqualsDimacs, assertCnfEqualsIgnoreVariables

from itertools import product


def test_op_empty():
    dimacs = """\
    p cnf 0 0
    """
    F = OrderingPrinciple(0)
    assertCnfEqualsDimacs(F, dimacs)


def test_op_one_element():
    dimacs = """\
    p cnf 0 1
    0
    """
    F = OrderingPrinciple(1)
    assertCnfEqualsDimacs(F, dimacs)


def test_gop_empty():
    G = CNF()
    graph = nx.Graph()
    F = GraphOrderingPrinciple(graph)
    assertCnfEqual(F, G)


def test_gop_complete():
    for total in (True, False):
        for smart in (True, False):
            for plant in (True, False):
                for knuth in (0, 2, 3):
                    graph = nx.complete_graph(4)
                    F = GraphOrderingPrinciple(graph, total, smart, plant,
                                               knuth)
                    G = OrderingPrinciple(4, total, smart, plant, knuth)
                    assertCnfEqualsIgnoreVariables(F, G)


def test_cli_op():
    for total, smart, plant, knuth in product((True, False), (True, False),
                                              (True, False), (False, 2, 3)):
        parameters = ["cnfgen", "-q", "op", "5"]
        if total:
            parameters.append("--total")
        if smart:
            parameters.append("--smart")
        if plant:
            parameters.append("--plant")
        if knuth:
            parameters.append("--knuth{}".format(knuth))
        switches = len([_f for _f in (total, smart, knuth) if _f])
        if (switches > 1):
            with pytest.raises(CLIError):
                cnfgen(parameters)
        else:
            F = OrderingPrinciple(5, total, smart, plant, knuth)
            assertCnfEqualsDimacs(F, cnfgen(parameters, mode='string'))


def test_cli_gop():
    for total, smart, plant, knuth in product((True, False), (True, False),
                                              (True, False), (False, 2, 3)):
        parameters = ["cnfgen", "-q", "gop", "--complete", "5"]
        if total:
            parameters.append("--total")
        if smart:
            parameters.append("--smart")
        if plant:
            parameters.append("--plant")
        if knuth:
            parameters.append("--knuth{}".format(knuth))
        switches = len([_f for _f in (total, smart, knuth) if _f])
        if (switches > 1):
            with pytest.raises(CLIError):
                cnfgen(parameters)
        else:
            graph = nx.complete_graph(5)
            F = GraphOrderingPrinciple(graph, total, smart, plant, knuth)
            assertCnfEqualsDimacs(F, cnfgen(parameters, mode='string'))
