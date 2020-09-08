import pytest

from cnfgen.clitools.graph_args import parse_graph_argument as P


def test_empty_args():
    with pytest.raises(ValueError):
        P('simple', '    ')


def test_consume_args():
    r = P('simple', 'grid 10 10 10')
    assert r['args'] == ['10', '10', '10']


def test_consume_args2():
    r = P(
        'simple',
        'grid 10 10 10 addedges 3 save dot grid.dot',
    )
    assert r['args'] == ['10', '10', '10']
    assert r['addedges'] == ['3']


def test_wrong_format():
    with pytest.raises(ValueError):
        P('simple', 'glrd 10 10 5 save file.matrix')


def test_two_constructions():
    with pytest.raises(ValueError):
        P('simple', 'gnp 10 .5 complete 5')


def test_just_a_file():
    P('simple', 'gnp 10 .5 save file.matrix')


def test_invalid_construction():
    with pytest.raises(ValueError):
        P('bipartite', 'nonsense 10 10')


def test_redundant_save_format():
    r = P('simple', 'complete 10 save dot file.dot')
    assert r['save'] == ['dot', 'file.dot']


def test_redundant_graph_format():
    r = P('simple', 'dot file.dot addedges 10')
    assert r['fileformat'] == 'dot'


def test_detect_graph_format():
    r = P('bipartite', 'file.matrix')
    assert r['fileformat'] == 'autodetect'
    assert r['filename'] == 'file.matrix'
