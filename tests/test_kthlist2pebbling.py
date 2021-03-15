import io

from cnfgen import PebblingFormula
from cnfgen import readGraph

from cnfgen import OrSubstitution
from cnfgen import XorSubstitution
from cnfgen import FormulaLifting

from cnfgen.clitools import kthlist2pebbling, CLIError
from tests.utils import redirect_stdin


def test_unit_graph():

    input = io.StringIO("1\n1 : 0\n")
    F = PebblingFormula(readGraph(input, 'dag', 'kthlist'))
    lib = F.to_dimacs()

    input.seek(0)
    with redirect_stdin(input):
        cli = kthlist2pebbling(["kthlist2pebbling", "-q", "none"],
                               mode='string')
    assert lib == cli


def test_small_line():

    input = io.StringIO("3\n1 : 0\n2 : 1 0\n3 : 2 0\n")
    F = PebblingFormula(readGraph(input, 'dag', 'kthlist'))
    lib = F.to_dimacs()

    input.seek(0)
    with redirect_stdin(input):
        cli = kthlist2pebbling(["kthlist2pebbling", "-q", "none"],
                               mode='string')
    assert lib == cli


def test_small_pyramid():
    input = io.StringIO("3\n1 : 0\n2 : 0\n3 : 1 2 0\n")
    F = PebblingFormula(readGraph(input, 'dag', 'kthlist'))
    lib = F.to_dimacs()

    input.seek(0)
    with redirect_stdin(input):
        cli = kthlist2pebbling(["kthlist2pebbling", "-q", "none"],
                               mode='string')
    assert lib == cli


def test_no_argument():
    input = io.StringIO("3\n1 : 0\n2 : 0\n3 : 1 2 0\n")
    F = PebblingFormula(readGraph(input, 'dag', 'kthlist'))
    lib = F.to_dimacs()

    input.seek(0)
    with redirect_stdin(input):
        cli = kthlist2pebbling(["kthlist2pebbling", "-q", "none"],
                               mode='string')
    assert lib == cli


def test_or_substitution():
    input = io.StringIO("3\n1 : 0\n2 : 0\n3 : 1 2 0\n")
    G = PebblingFormula(readGraph(input, 'dag', 'kthlist'))
    F = OrSubstitution(G, 2)
    lib = F.to_dimacs()

    input.seek(0)
    with redirect_stdin(input):
        cli = kthlist2pebbling(["kthlist2pebbling", "-q", "or", "2"],
                               mode='string')
    assert lib == cli


def test_lift_substitution():
    input = io.StringIO("3\n1 : 0\n2 : 0\n3 : 1 2 0\n")
    G = PebblingFormula(readGraph(input, 'dag', 'kthlist'))
    F = FormulaLifting(G, 3)
    lib = F.to_dimacs()

    input.seek(0)
    with redirect_stdin(input):
        cli = kthlist2pebbling(["kthlist2pebbling", "-q", "lift", "3"],
                               mode='string')
    assert lib == cli


def test_xor_substitution():
    input = io.StringIO("3\n1 : 0\n2 : 0\n3 : 1 2 0\n")
    G = PebblingFormula(readGraph(input, 'dag', 'kthlist'))
    F = XorSubstitution(G, 2)
    input.seek(0)
    lib = F.to_dimacs()

    with redirect_stdin(input):
        cli = kthlist2pebbling(["kthlist2pebbling", "-q", "xor", "2"],
                               mode='string')
    assert lib == cli
