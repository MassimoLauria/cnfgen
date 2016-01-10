#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of the pigeonhole principle formulas
"""

from cnfformula.cnf import CNF
from cnfformula.cmdline import BipartiteGraphHelper

import cnfformula.cmdline
import cnfformula.families

from itertools import combinations,product

@cnfformula.families.register_cnf_generator
def PigeonholePrinciple(pigeons,holes,functional=False,onto=False):
    """Pigeonhole Principle CNF formula

    The pigeonhole  principle claims  that no M  pigeons can sit  in N
    pigeonholes  without collision  if M>N.   The  counterpositive CNF
    formulation  requires  such mapping  to  be  satisfied. There  are
    different  variants of this  formula, depending  on the  values of
    `functional` and `onto` argument.

    - PHP: pigeon can sit in multiple holes
    - FPHP: each pigeon sits in exactly one hole
    - onto-PHP: pigeon can  sit in multiple holes, every  hole must be
                covered.
    - Matching: one-to-one bijection between pigeons and holes.

    Arguments:
    - `pigeon`: number of pigeons
    - `hole`:   number of holes
    - `functional`: add clauses to enforce at most one hole per pigeon
    - `onto`: add clauses to enforce that any hole must have a pigeon

    >>> print(PigeonholePrinciple(4,3).dimacs(export_header=False))
    p cnf 12 22
    1 2 3 0
    4 5 6 0
    7 8 9 0
    10 11 12 0
    -1 -4 0
    -1 -7 0
    -1 -10 0
    -4 -7 0
    -4 -10 0
    -7 -10 0
    -2 -5 0
    -2 -8 0
    -2 -11 0
    -5 -8 0
    -5 -11 0
    -8 -11 0
    -3 -6 0
    -3 -9 0
    -3 -12 0
    -6 -9 0
    -6 -12 0
    -9 -12 0
    """
    if functional:
        if onto:
            formula_name="Matching"
        else:
            formula_name="Functional pigeonhole principle"
    else:
        if onto:
            formula_name="Onto pigeonhole principle"
        else:
            formula_name="Pigeonhole principle"

    # Clause generator
    def _PHP_clause_generator(pigeons,holes,functional,onto):
        """Generator for the clauses"""
        # Pigeon axioms
        for p in xrange(1,pigeons+1):
            yield [ (True,'p_{{{0},{1}}}'.format(p,h)) for h in xrange(1,holes+1)]
        # Onto axioms
        if onto:
            for h in xrange(1,holes+1):
                yield [ (True,'p_{{{0},{1}}}'.format(p,h)) for p in xrange(1,pigeons+1)]
        # No conflicts axioms
        for h in xrange(1,holes+1):
            for (p1,p2) in combinations(range(1,pigeons+1),2):
                yield [ (False,'p_{{{0},{1}}}'.format(p1,h)),
                        (False,'p_{{{0},{1}}}'.format(p2,h)) ]
        # Function axioms
        if functional:
            for p in xrange(1,pigeons+1):
                for (h1,h2) in combinations(range(1,holes+1),2):
                    yield [ (False,'p_{{{0},{1}}}'.format(p,h1)),
                            (False,'p_{{{0},{1}}}'.format(p,h2)) ]

    php=CNF()
    php.header="{0} formula for {1} pigeons and {2} holes\n".format(formula_name,pigeons,holes)\
        + php.header

    for p in xrange(1,pigeons+1):
        for h in xrange(1,holes+1):
            php.add_variable('p_{{{0},{1}}}'.format(p,h))
    
    clauses=_PHP_clause_generator(pigeons,holes,functional,onto)
    for c in clauses:
        php.add_clause(c,strict=True)

    return php

@cnfformula.families.register_cnf_generator
def GraphPigeonholePrinciple(graph,functional=False,onto=False):
    """Graph Pigeonhole Principle CNF formula

    The graph pigeonhole principle CNF formula, defined on a bipartite
    graph G=(L,R,E), claims that there is a subset E' of the edges such that 
    every vertex on the left size L has at least one incident edge in E' and 
    every edge on the right side R has at most one incident edge in E'.

    This is possible only if the graph has a matching of size |L|.

    There are different variants of this formula, depending on the
    values of `functional` and `onto` argument.

    - PHP(G):  each left vertex can be incident to multiple edges in E'
    - FPHP(G): each left vertex must be incident to exaclty one edge in E'
    - onto-PHP: all right vertices must be incident to some vertex
    - matching: E' must be a perfect matching between L and R

    Arguments:
    - `graph` : bipartite graph
    - `functional`: add clauses to enforce at most one edge per left vertex
    - `onto`: add clauses to enforce that any right vertex has one incident edge


    Remark: the graph vertices must have the 'bipartite' attribute
    set. Left vertices must have it set to 0 and the right ones to
    1. Any vertex without the attribute is ignored.

    """
    if functional:
        if onto:
            formula_name="Graph matching"
        else:
            formula_name="Graph functional pigeonhole principle"
    else:
        if onto:
            formula_name="Graph onto pigeonhole principle"
        else:
            formula_name="Graph pigeonhole principle"

    Left  =  [v for v in graph.nodes() if graph.node[v].get("bipartite")==0]
    Right =  [v for v in graph.nodes() if graph.node[v].get("bipartite")==1]
            
    # Clause generator
    def _GPHP_clause_generator(G,functional,onto):
        # Pigeon axioms
        for p in Left:
            yield [ (True,'p_{{{0},{1}}}'.format(p,h)) for h in G.adj[p]]
        # Onto axioms
        if onto:
            for h in Right:
                yield [ (True,'p_{{{0},{1}}}'.format(p,h)) for p in G.adj[h]]
        # No conflicts axioms
        for h in Right:
            for (p1,p2) in combinations(G.adj[h],2):
                yield [ (False,'p_{{{0},{1}}}'.format(p1,h)),
                        (False,'p_{{{0},{1}}}'.format(p2,h)) ]
        # Function axioms
        if functional:
            for p in Left:
                for (h1,h2) in combinations(G.adj[p],2):
                    yield [ (False,'p_{{{0},{1}}}'.format(p,h1)),
                            (False,'p_{{{0},{1}}}'.format(p,h2)) ]

    gphp=CNF()
    gphp.header="{0} formula for graph {1}\n".format(formula_name,graph.name)

    for p in Left:
        for h in graph.adj[p]:
            gphp.add_variable('p_{{{0},{1}}}'.format(p,h))

    
    clauses=_GPHP_clause_generator(graph,functional,onto)
    for c in clauses:
        gphp.add_clause(c,strict=True)

    return gphp


@cnfformula.families.register_cnf_generator
def RelativizedPigeonholePrinciple(pigeons,holes,resting_places):
    """Relativized Pigeonhole Principle CNF formula

    A description can be found in [1]_

    Arguments:
    - `pigeons`: number of pigeons
    - `holes`: number of holes
    - `resting_places`: number of resting places

    References
    ----------
    .. [1] A. Atserias, M. Lauria and J. Nordström
           Narrow Proofs May Be Maximally Long
           IEEE Conference on Computational Complexity 2014

    """
    formula_name="Relativized Pigeonhole principle"

    php=CNF()
    php.header="{0} formula for {1} pigeons and {2} holes with {3} resting places\n".format(formula_name,pigeons,holes,resting_places)\
        + php.header

    def P(u,v): return 'p_{{{0},{1}}}'.format(u,v)
    def Q(v,w): return 'q_{{{0},{1}}}'.format(v,w)
    def R(v): return 'r_{{{0}}}'.format(v)
    U = xrange(1, 1 + pigeons)
    V = xrange(1, 1 + resting_places)
    W = xrange(1, 1 + holes)
    for u,v in product(U,V): php.add_variable(P(u,v))
    for v,w in product(V,W): php.add_variable(Q(v,w))
    for v in V: php.add_variable(R(v))

    # NOTE: the order of ranges in the products are chosen such that related clauses appear after each other
    # (3.1a) p[u,1] v p[u,2] v ... v p[u,n] for all u \in [k]
    for u in U: php.add_clause([(True, P(u,v)) for v in V], strict=True)
    # (3.1b) ~p[u,v] v ~p[u',v] for all u, u' \in [k], u != u', v \in [n]
    for (v, (u, u_)) in product(V, combinations(U, 2)): php.add_clause([(False, P(u,v)), (False, P(u_,v))], strict=True)
    # (3.1c) ~p[u,v] v r[v] for all u \in [k], v \in [n]
    for (v, u) in product(V, U): php.add_clause([(False, P(u,v)), (True, R(v))], strict=True)
    # (3.1d) ~r[v] v q[v,1] v ... v q[v,k-1] for all v \in [n]
    for v in V: php.add_clause([(False, R(v))] + [(True, Q(v,w)) for w in W], strict=True)
    # (3.1e) ~r[v] v ~r[v'] v ~q[v,w] v ~q[v',w] for all v, v' \in [n], v != v', w \in [k-1]
    for (w, (v, v_)) in product(W, combinations(V, 2)): php.add_clause([(False, R(v)), (False, R(v_)), (False, Q(v,w)), (False, Q(v_,w))], strict=True)

    return php

@cnfformula.cmdline.register_cnfgen_subcommand
class PHPCmdHelper(object):
    """Command line helper for the Pigeonhole principle CNF"""
    
    name='php'
    description='pigeonhole principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for pigeonhole principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('pigeons',metavar='<pigeons>',type=int,help="Number of pigeons")
        parser.add_argument('holes',metavar='<holes>',type=int,help="Number of holes")
        parser.add_argument('--functional',action='store_true',
                            help="pigeons sit in at most one hole")
        parser.add_argument('--onto',action='store_true',
                            help="every hole has a sitting pigeon")

    @staticmethod
    def build_cnf(args):
        """Build a PHP formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return PigeonholePrinciple(args.pigeons,
                                   args.holes,
                                   functional=args.functional,
                                   onto=args.onto)


@cnfformula.cmdline.register_cnfgen_subcommand
class GPHPCmdHelper:
    """Command line helper for the Pigeonhole principle on graphs"""

    name='gphp'
    description='graph pigeonhole principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for pigeonhole principle formula over graphs

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('--functional',action='store_true',
                            help="pigeons sit in at most one hole")
        parser.add_argument('--onto',action='store_true',
                            help="every hole has a sitting pigeon")
        BipartiteGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build a Graph PHP formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G = BipartiteGraphHelper.obtain_graph(args) 
        return GraphPigeonholePrinciple(G,
                                        functional=args.functional,
                                        onto=args.onto)


@cnfformula.cmdline.register_cnfgen_subcommand
class RPHPCmdHelper(object):
    """Command line helper for the Relativized Pigeonhole principle CNF"""

    name='rphp'
    description='relativized pigeonhole principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for relativized pigeonhole principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('pigeons',metavar='<pigeons>',type=int,help="Number of pigeons")
        parser.add_argument('holes',metavar='<holes>',type=int,help="Number of holes")
        parser.add_argument('resting_places',metavar='<resting-places>',type=int,help="Number of resting places")

    @staticmethod
    def build_cnf(args):
        """Build a RPHP formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return RelativizedPigeonholePrinciple(args.pigeons, args.holes, args.resting_places)



