import pytest

from cnfgen.clitools.graph_cmdline import SimpleGraphHelper
from cnfgen.clitools.cmdline import CLIParser, CLIError


def get_graph(args):
    parser = CLIParser()
    SimpleGraphHelper.setup_command_line(parser)
    args = parser.parse_args(args)
    return SimpleGraphHelper.obtain_graph(args)


def test_gnp():
    G = get_graph(["--gnp", "10", "0.5"])
    assert G.order() == 10


def test_gnm():
    G = get_graph(["--gnm", "10", "15"])
    assert G.order() == 10
    assert G.size() == 15


def test_gnd_fail():
    with pytest.raises(CLIError):
        G = get_graph(["--gnd", "9", "3"])


def test_complete():
    G = get_graph(["--complete", "10"])
    assert G.order() == 10
    assert G.size() == 45
    for v in G.nodes():
        assert G.degree(v) == 9


def test_grid():
    G = get_graph(["--grid", "8", "5"])
    assert G.order() == 40
    degrees = sorted([G.degree(v) for v in G.nodes()])

    assert degrees == [2] * 4 + [3] * (3 + 3 + 6 + 6) + [4] * (3 * 6)


def test_torus():
    G = get_graph(["--torus", "8", "5"])
    assert G.order() == 40

    for v in G.nodes():
        assert G.degree(v) == 4


def test_already_complete():
    with pytest.raises(ValueError):
        get_graph(["--complete", "10", "--addedges", "1"])


def test_empty_to_complete():
    G = get_graph(["--gnp", "10", "0", "--addedges", "45"])
    assert G.order() == 10
    assert G.size() == 45
    for v in G.nodes():
        assert G.degree(v) == 9


def test_add_edges():
    G = get_graph(["--gnm", "10", "15", "--addedges", "10"])
    assert G.order() == 10
    assert G.size() == 25


def test_plant_too_large():
    with pytest.raises(ValueError):
        get_graph(["--complete", "10", "--plantclique", "11"])


def test_already_complete():
    G = get_graph(["--complete", "10", "--plantclique", "5"])
    assert G.order() == 10
    assert G.size() == 45


def test_complete_with_planted():
    G = get_graph(["--gnp", "10", "0", "--plantclique", "10"])
    assert G.order() == 10
    assert G.size() == 45


def test_plant_clique():
    G = get_graph(["--gnm", "10", "15", "--plantclique", "6"])
    assert G.order() == 10
    assert 15 <= G.size() <= 30
