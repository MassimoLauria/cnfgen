#!/usr/bin/env python
"""Graph constructions that are available on the command line

Copyright (C) 2020  Massimo Lauria <massimo.lauria@uniroma1.it>
https://github.com/MassimoLauria/cnfgen.git
"""

import random
import networkx
from itertools import combinations

from networkx.algorithms.bipartite import complete_bipartite_graph
from networkx.algorithms.bipartite import random_graph as bipartite_random_graph
from networkx.algorithms.bipartite import gnmk_random_graph as bipartite_gnmk_random_graph

from cnfgen.graphs import bipartite_random_left_regular, bipartite_random_regular, bipartite_shift

from cnfgen.graphs import sample_missing_edges


#
# Simple graphs
#
def obtain_gnd(parsed):
    """Build a graph according to gnd construction"""
    try:
        n, d = parsed['args']
        n = int(n)
        d = int(d)
        assert n > 0
        assert d > 0
    except (TypeError, AssertionError, ValueError):
        raise ValueError('\'gnd\' expects arguments <N> <D> with N>0, D>0')

    if (n * d) % 2 == 1:
        raise ValueError('\'gnd\' expects arguments <N> <D> with even N * D')

    G = networkx.random_regular_graph(d, n)
    G.name = 'Random {}-regular graph of {} vertices'.format(d, n)
    return G


def obtain_gnp(parsed):
    """Build a graph according to gnp construction"""
    try:
        n, p = parsed['args']
        n = int(n)
        p = float(p)
        assert n > 0
        assert 0 <= p <= 1
    except (TypeError, ValueError, AssertionError):
        raise ValueError(
            '\'gnp\' expects arguments <N> <p> with N>0, p in [0,1]')

    G = networkx.gnp_random_graph(n, p)
    G.name = 'Random {}-biased graph of {} vertices'.format(p, n)
    return G


def obtain_gnm(parsed):
    """Build a graph according to gnm construction"""
    try:
        n, m = parsed['args']
        n = int(n)
        m = int(m)
        assert n > 0
        assert m >= 0
        assert m <= n * (n - 1) // 2
    except (TypeError, ValueError, AssertionError):
        raise ValueError(
            '\'gnm\' expects arguments <N> <M> with N>0 and 0 <= M <= N(N-1)/2'
        )

    G = networkx.gnm_random_graph(n, m)
    G.name = 'Random graph of {} vertices with {} edges'.format(n, m)
    return G


def obtain_complete_simple(parsed):
    """Build a simple complete graph"""
    try:
        if len(parsed['args']) != 1:
            raise ValueError
        n = int(parsed['args'][0])
        assert n > 0
    except (TypeError, ValueError, AssertionError):
        raise ValueError('\'complete\' expects argument <N> with N>0')

    G = networkx.complete_graph(n)
    G.name = "Complete graphs of {} vertices".format(n)
    return G


def obtain_empty_simple(parsed):
    """Build a simple empty graph"""
    try:
        if len(parsed['args']) != 1:
            raise ValueError
        n = int(parsed['args'][0])
        assert n > 0
    except (TypeError, ValueError, AssertionError):
        raise ValueError('\'complete\' expects argument <N> with N>0')

    G = networkx.empty_graph(n)
    G.name = "Empty graphs of {} vertices".format(n)
    return G


def obtain_grid_or_torus(parsed, periodic):
    """Build a graph according to grid/toris construction"""
    dimensions = parsed['args']
    if periodic:
        name = 'torus'
    else:
        name = 'grid'
    try:
        dimensions = [int(x) for x in dimensions]
        for d in dimensions:
            if d <= 0:
                raise ValueError
    except (TypeError, ValueError):
        raise ValueError(
            'Dimensions d1 x ... x dn of a {} must be positive integer'.format(
                name))

    G = networkx.grid_graph(dimensions, periodic=periodic)
    G.name = "{} graph of dimension {}".format(name, dimensions)
    return G


def obtain_grid(parsed):
    return obtain_grid_or_torus(parsed, periodic=False)


def obtain_torus(parsed):
    return obtain_grid_or_torus(parsed, periodic=True)


def modify_simple_graph_plantclique(parsed, G):
    try:
        if len(parsed['plantclique']) != 1:
            raise ValueError
        cliquesize = int(parsed['plantclique'][0])
        assert cliquesize >= 0
    except (TypeError, ValueError, AssertionError):
        raise ValueError('\'plantclique\' expects argument <k> with k>=0')

    if cliquesize > G.order():
        raise ValueError("Planted clique cannot be larger than graph")

    clique = random.sample(G.nodes(), cliquesize)

    for v, w in combinations(clique, 2):
        G.add_edge(v, w)
    G.name += " + planted {}-clique".format(cliquesize)
    return G


def modify_simple_graph_addedges(parsed, G):
    try:
        if len(parsed['addedges']) != 1:
            raise ValueError
        k = int(parsed['addedges'][0])
        assert k >= 0
    except (TypeError, ValueError, AssertionError):
        raise ValueError('\'addedges\' expects argument <k> with k>=0')

    G.add_edges_from(sample_missing_edges(G, k))
    G.name += " + {} random edges".format(k)
    return G


#
# Bipartite graphs
#
def obtain_glrp(parsed):
    """Build a random bipartite with independently sampled edges"""
    try:
        left, right, p = parsed['args']
        left = int(left)
        right = int(right)
        p = float(p)
        assert left > 0
        assert right > 0
        assert 0 <= p <= 1
    except (TypeError, ValueError, AssertionError):
        raise ValueError(
            '\'glrp\' expects three arguments <L> <R> <p>\n with L>0, R>0, p in [0,1]'
        )
    G = bipartite_random_graph(left, right, p)
    G.name = 'Random {}-biased bipartite with ({},{}) vertices'.format(
        p, left, right)
    return G


def obtain_glrm(parsed):
    """Build a random bipartite with a fixed number of sampled edges"""
    try:
        left, right, edges = parsed['args']
        left = int(left)
        right = int(right)
        edges = int(edges)
        assert left > 0
        assert right > 0
        assert 0 <= edges <= left * right
    except (TypeError, ValueError, AssertionError):
        raise ValueError(
            '\'glrm\' expects three arguments <L> <R> <m>\n with L>0, R>0, 0<= m <= L*R'
        )
    G = bipartite_gnmk_random_graph(left, right, edges)
    G.name = 'Random bipartite with ({},{}) vertices and {} edges'.format(
        left, right, edges)
    return G


def obtain_glrd(parsed):
    """Build a random bipartite with a fixed degree of the left side"""
    try:
        left, right, degree = parsed['args']
        left = int(left)
        right = int(right)
        degree = int(degree)
        assert left > 0
        assert right > 0
        assert 0 <= degree <= right
    except (TypeError, ValueError, AssertionError):
        raise ValueError(
            '\'glrd\' expects three arguments <L> <R> <d>\n with L>0, R>0, 0<= d <= R'
        )
    G = bipartite_random_left_regular(left, right, degree)
    G.name = "Random {}-left regular bipartite with ({},{}) vertices".format(
        degree, left, right)
    return G


def obtain_bipartite_regular(parsed):
    """Build a random bipartite, regular on both sides"""
    try:
        left, right, degree = parsed['args']
        left = int(left)
        right = int(right)
        degree = int(degree)
        assert left > 0
        assert right > 0
        assert 0 <= degree <= right
        assert (degree * left % right) == 0
    except (TypeError, ValueError, AssertionError):
        raise ValueError('\'regular\' expects three arguments <L> <R> <d>\n'
                         'with L>0, R>0, 0<= d <= R\n'
                         'where R divides L*d')
    G = bipartite_random_regular(left, right, degree)
    G.name = "Random regular bipartite with ({},{}) vertices and left degree {}".format(
        left, right, degree)
    return G


def obtain_bipartite_shift(parsed):
    """Build a bipartite graph where edges follow a fixed pattern"""
    values = parsed['args']
    if len(values) < 2:
        raise ValueError(
            "'shift' requires two or more positive int parameters.")

    try:
        N, M, pattern = int(values[0]), int(values[1]), sorted(
            int(x) for x in values[2:])

        assert N > 0
        assert M > 0

        for i in range(len(pattern) - 1):
            if pattern[i] == pattern[i + 1]:
                raise ValueError

        if any([x < 0 or x > M for x in pattern]):
            raise ValueError
    except (TypeError, ValueError, AssertionError):
        raise ValueError(
            '\'shift\' expect args <N> <M> <v1> <v2> ... \nThe results is an (N,M) bipartite.\nVertex i connexted to i+v1, i+v2,... (mod M)\n<v1> <v2> ... must not have repetitions and be between 0 and M'
        )

    G = bipartite_shift(N, M, pattern)
    G.name = 'Bipartite with {},{} vertices and shifting edge pattern {}'.format(
        N, M, pattern)
    return G


def obtain_complete_bipartite(parsed):
    """Build a bipartite complete graph"""
    try:
        if len(parsed['args']) != 2:
            raise ValueError
        left = int(parsed['args'][0])
        right = int(parsed['args'][1])
        assert left > 0
        assert right > 0
    except (TypeError, ValueError, AssertionError):
        raise ValueError('\'complete\' expects argument <L> <R> with L>0, R>0')

    G = complete_bipartite_graph(left, right)
    G.name = "Complete bipartite graph with ({},{}) vertices".format(
        left, right)
    return G


def obtain_empty_bipartite(parsed):
    """Build an empty complete graph"""
    try:
        if len(parsed['args']) != 2:
            raise ValueError
        left = int(parsed['args'][0])
        right = int(parsed['args'][1])
        assert left > 0
        assert right > 0
    except (TypeError, ValueError, AssertionError):
        raise ValueError('\'complete\' expects argument <L> <R> with L>0, R>0')

    G = bipartite_gnmk_random_graph(left, right, 0)
    G.name = "Empty bipartite graph with ({},{}) vertices".format(left, right)
    return G
