#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of counting/matching formulas
"""

from cnfformula.cnf import CNF
from cnfformula.cmdline import SimpleGraphHelper

from cnfformula.cmdline  import register_cnfgen_subcommand
from cnfformula.families import register_cnf_generator

from cnfformula.cnf import equal_to_constraint
from itertools import combinations


@register_cnf_generator
def CountingPrinciple(M,p):
    """Generates the clauses for the counting matching principle.
    
    The principle claims that there is a way to partition M in sets of
    size p each.

    Arguments:
    - `M`  : size of the domain
    - `p`  : size of each class

    """
    cnf=CNF()

    # Describe the formula
    name="Counting Principle: {0} divided in parts of size {1}.".format(M,p)
    cnf.header=name+"\n"+cnf.header

    def var_name(tpl):
        return "Y_{{"+",".join("{0}".format(v) for v in tpl)+"}}"

    # Incidence lists
    incidence=[[] for _ in range(M)]
    for tpl in combinations(range(M),p):
        for i in tpl:
            incidence[i].append(tpl)
    
    # Each element of the domain is in exactly one part.
    for el in range(M):

        edge_vars = [var_name(tpl) for tpl in incidence[el]]

        for cls in equal_to_constraint(edge_vars,1):
            cnf.add_clause(cls)

    return cnf


@register_cnf_generator
def PerfectMatchingPrinciple(graph):
    """Generates the clauses for the graph perfect matching principle.
    
    The principle claims that there is a way to select edges to such
    that all vertices have exactly one incident edge set to 1.

    Arguments:
    - `graph`  : undirected graph

    """
    cnf=CNF()

    # Describe the formula
    name="Perfect Matching Principle"
    
    if hasattr(graph,'name'):
        cnf.header=name+" of graph:\n"+graph.name+"\n"+cnf.header
    else:
        cnf.header=name+".\n"+cnf.header

    def var_name(u,v):
        if u<=v:
            return 'x_{{{0},{1}}}'.format(u,v)
        else:
            return 'x_{{{0},{1}}}'.format(v,u)
            
    # Each vertex has exactly one edge set to one.
    for v in graph.nodes():

        edge_vars = [var_name(u,v) for u in graph.adj[v]]

        for cls in equal_to_constraint(edge_vars,1):
            cnf.add_clause(cls)

    return cnf





@register_cnfgen_subcommand
class ParityCmdHelper(object):
    """Command line helper for Parity Principle formulas
    """
    name='parity'
    description='parity principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Parity Principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('N',metavar='<N>',type=int,help="domain size")

    @staticmethod
    def build_cnf(args):
        return CountingPrinciple(args.N,2)


@register_cnfgen_subcommand
class PMatchingCmdHelper(object):
    """Command line helper for Perfect Matching Principle formulas
    """
    name='matching'
    description='perfect matching principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Perfect Matching Principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        G = SimpleGraphHelper.obtain_graph(args)
        return PerfectMatchingPrinciple(G)


@register_cnfgen_subcommand
class CountingCmdHelper:
    """Command line helper for Counting Principle formulas
    """
    name='count'
    description='counting principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Counting Principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('M',metavar='<M>',type=int,help="domain size")
        parser.add_argument('p',metavar='<p>',type=int,help="size of the parts")

    @staticmethod
    def build_cnf(args):
        """Build an Counting Principle formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return CountingPrinciple(args.M,args.p)

    
