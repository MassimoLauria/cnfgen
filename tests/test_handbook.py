# This tests check that the command lines written in the
# handbook of satisfiability are well tested.
import pytest

from cnfgen.clitools import cnfgen, CLIError


def test_php_cli():
    F = cnfgen(['cnfgen', 'php', 5], mode='formula')
    assert F.number_of_variables() == 30
    assert len(F) == 6 + 15 * 5
    assert not F.is_satisfiable()[0]
    F = cnfgen(['cnfgen', 'php', 8, 5], mode='formula')
    assert F.number_of_variables() == 40
    assert len(F) == 8 + 28 * 5
    assert not F.is_satisfiable()[0]
    F = cnfgen(['cnfgen', 'php', '--functional', 8, 5], mode='formula')
    assert F.number_of_variables() == 40
    assert len(F) == 8 + 28 * 5 + 10 * 8
    assert not F.is_satisfiable()[0]
    F = cnfgen(['cnfgen', 'php', '--onto', 8, 5], mode='formula')
    assert F.number_of_variables() == 40
    assert len(F) == 8 + 5 + 28 * 5
    assert not F.is_satisfiable()[0]
    F = cnfgen(['cnfgen', 'php', '--onto', '--functional', 8, 5],
               mode='formula')
    assert F.number_of_variables() == 40
    assert len(F) == 8 + 5 + 28 * 5 + 10 * 8
    assert not F.is_satisfiable()[0]


def test_gphp_cli():
    F = cnfgen(['cnfgen', 'php', 8, 5, 3], mode='formula')
    for c in F:
        assert len(c) <= 3
    assert F.number_of_variables() == 24
    assert len(F) <= 8 + 28 * 5
    assert not F.is_satisfiable()[0]
    F = cnfgen(['cnfgen', 'php', '--functional', 8, 5, 3], mode='formula')
    for c in F:
        assert len(c) <= 3
    assert F.number_of_variables() == 24
    assert len(F) <= 8 + 28 * 5 + 10 * 8
    assert not F.is_satisfiable()[0]
    F = cnfgen(['cnfgen', 'php', '--onto', 8, 5, 3], mode='formula')
    assert F.number_of_variables() == 24
    assert len(F) <= 8 + 5 + 28 * 5
    assert not F.is_satisfiable()[0]
    F = cnfgen(['cnfgen', 'php', '--onto', '--functional', 8, 5, 3],
               mode='formula')
    assert F.number_of_variables() == 24
    assert len(F) <= 8 + 5 + 28 * 5 + 10 * 8
    assert not F.is_satisfiable()[0]


def test_parity_cli(shared_datadir):
    F = cnfgen(['cnfgen', 'parity', 8], mode='formula')
    assert F.is_satisfiable()[0]
    F = cnfgen(['cnfgen', 'parity', 5], mode='formula')
    assert not F.is_satisfiable()[0]
    cnfgen(['cnfgen', 'matching', 'gnd', 10, 3], mode='formula')
    with pytest.raises(CLIError):
        cnfgen(['cnfgen', 'matching', 'gnd', 9, 3], mode='formula')
    F = cnfgen(
        ['cnfgen', 'matching', shared_datadir / 'oddvertices_gnd_15_4.gml'],
        mode='formula')
    assert not F.is_satisfiable()[0]


def test_tseitin_cli(shared_datadir):
    F = cnfgen(['cnfgen', 'tseitin', 8, 3], mode='formula')
    assert not F.is_satisfiable()[0]
    for c in F:
        assert len(c) == 3
    assert len(F) == 8 * 2**3 // 2

    F = cnfgen(['cnfgen', 'tseitin', 8], mode='formula')
    assert not F.is_satisfiable()[0]
    for c in F:
        assert len(c) == 4
    assert len(F) == 8 * 2**4 // 2

    F = cnfgen(['cnfgen', 'tseitin', 'randomodd', 'grid', 4, 4],
               mode='formula')
    assert not F.is_satisfiable()[0]

    F = cnfgen(['cnfgen', 'tseitin', 'randomeven', 'grid', 4, 4],
               mode='formula')
    assert F.is_satisfiable()[0]

    cnfgen(
        ['cnfgen', 'tseitin', 'randomodd', shared_datadir / 'gnm_10_30.gml'],
        mode='formula')


def test_randkcnf_cli():
    F = cnfgen(['cnfgen', 'randkcnf', 3, 10, 7], mode='formula')
    assert F.number_of_variables() == 10
    assert len(F) == 7
    for c in F:
        assert len(c) == 3

    F = cnfgen(['cnfgen', 'randkcnf', 4, 10, 7], mode='formula')
    assert F.number_of_variables() == 10
    assert len(F) == 7
    for c in F:
        assert len(c) == 4

    F = cnfgen(['cnfgen', 'randkcnf', 6, 15, 4], mode='formula')
    assert F.number_of_variables() == 15
    assert len(F) == 4
    for c in F:
        assert len(c) == 6

    with pytest.raises(CLIError):
        cnfgen(['cnfgen', 'randkcnf', 10, 1, 14], mode='formula')


def test_kcolor_cli(shared_datadir):
    F = cnfgen(['cnfgen', 'kcolor', 4, 'gnd', 10, 3], mode='formula')
    assert F.is_satisfiable()[0]
    F = cnfgen(['cnfgen', 'kcolor', 4, 'gnp', 10, .3], mode='formula')
    cnfgen(
        ['cnfgen', 'kcolor', 3, shared_datadir / 'oddvertices_gnd_15_4.gml'],
        mode='formula')


def test_kclique_cli(shared_datadir):
    cnfgen(['cnfgen', 'kclique', 4, 'gnd', 15, 6], mode='formula')
    F = cnfgen(['cnfgen', 'kclique', 4, 'gnd', 16, 3, 'plantclique', 4],
               mode='formula')
    assert F.is_satisfiable()[0]
    F = cnfgen(['cnfgen', 'kclique', 4, 'gnp', 10, .3], mode='formula')
    F = cnfgen(
        ['cnfgen', 'kclique', 5, shared_datadir / 'oddvertices_gnd_15_4.gml'],
        mode='formula')
    assert not F.is_satisfiable()[0]


def test_subsetcard_cli(shared_datadir):
    F = cnfgen(['cnfgen', 'subsetcard', 10], mode='formula')
    for c in F:
        assert len(c) == 3
    assert not F.is_satisfiable()[0]
    F = cnfgen(['cnfgen', 'subsetcard', 10, 4], mode='formula')
    for c in F:
        len(c) == 3
    assert not F.is_satisfiable()[0]
    F = cnfgen(['cnfgen', 'subsetcard', 10, 6], mode='formula')
    for c in F:
        assert len(c) == 4
    cnfgen(['cnfgen', 'subsetcard', shared_datadir / 'graph.matrix'],
           mode='formula')


def test_op_cli(shared_datadir):
    F = cnfgen(['cnfgen', 'op', 5], mode='formula')
    assert not F.is_satisfiable()[0]
    F = cnfgen(['cnfgen', 'op', '--total', 5], mode='formula')
    assert not F.is_satisfiable()[0]
    F = cnfgen(['cnfgen', 'op', 10, 3], mode='formula')
    assert not F.is_satisfiable()[0]
    for c in F:
        assert len(c) <= 3
    F = cnfgen(['cnfgen', 'op', '--total', 10, 3], mode='formula')
    assert not F.is_satisfiable()[0]
    for c in F:
        assert len(c) <= 3
    F = cnfgen(['cnfgen', 'op', 10, 5], mode='formula')
    assert not F.is_satisfiable()[0]
    for c in F:
        assert len(c) <= 5


def test_peb_cli(shared_datadir):
    F = cnfgen(['cnfgen', 'peb', 'pyramid', 5], mode='formula')
    assert F.number_of_variables() == 21
    assert not F.is_satisfiable()[0]

def test_peb_cli_xor(shared_datadir):
    F = cnfgen(['cnfgen', 'peb', 'pyramid', 5, '-T', 'xor', 2], mode='formula')
    assert F.number_of_variables() == 42
    assert not F.is_satisfiable()[0]

def test_peb_cli_lift(shared_datadir):
    F = cnfgen(['cnfgen', 'peb', 'pyramid', 2, '-T', 'lift', 3],
               mode='formula')
    assert F.number_of_variables() == 36
    assert not F.is_satisfiable()[0]

def test_peb_cli_or(shared_datadir):
    F = cnfgen(['cnfgen', 'peb', 'pyramid', 5, '-T', 'or', 2], mode='formula')
    assert F.number_of_variables() == 42
    assert not F.is_satisfiable()[0]

def test_peb_cli_read(shared_datadir):
    F = cnfgen(['cnfgen', 'peb', shared_datadir / 'dag.gml', '-T', 'xor', 2],
               mode='formula')
    assert not F.is_satisfiable()[0]


def test_ec_cli():
    with pytest.raises(CLIError):
        cnfgen(['cnfgen', 'ec', 'gnd', 10, 5], mode='formula')
    F = cnfgen(['cnfgen', 'ec', 'gnd', 10, 6], mode='formula')
    assert F.is_satisfiable()[0]
    F = cnfgen(['cnfgen', 'ec', 'gnd', 9, 6], mode='formula')
    assert not F.is_satisfiable()[0]
    F = cnfgen(['cnfgen', 'ec', 'complete', 5], mode='formula')
    assert F.is_satisfiable()[0]


def test_cliquecoloring_cli():
    with pytest.raises(CLIError):
        cnfgen(['cnfgen', 'cliquecoloring', 6, -3, 5], mode='formula')
    F = cnfgen(['cnfgen', 'cliquecoloring', 6, 4, 3], mode='formula')
    assert not F.is_satisfiable()[0]
    F = cnfgen(['cnfgen', 'cliquecoloring', 7, 3, 2], mode='formula')
    assert not F.is_satisfiable()[0]
