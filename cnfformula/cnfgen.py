#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function

from cnfformula import CNF
from cnfformula import TransformFormula,available_transform

from cnfformula.graphs import supported_formats as graph_formats
from cnfformula.graphs import readDigraph,readGraph,writeGraph


from cnfformula.families import (
    PigeonholePrinciple,
    PebblingFormula,
    OrderingPrinciple,
    GraphOrderingPrinciple,
    RamseyNumber,
    TseitinFormula,
    SubgraphFormula,
    ColoringFormula)



__docstring__ =\
"""Utilities to build CNF formulas interesting for proof complexity.

The module `cnfgen`  contains facilities to generate  cnf formulas, in
order to  be printed  in dimacs  or LaTeX  formats. Such  formulas are
ready to be  fed to sat solvers.  In particular  the module implements
both a library of CNF generators and a command line utility.

Copyright (C) 2012, 2013, 2014  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git


Create you own CNFs:

>>> c=CNF([ [(True,"x1"),(True,"x2"),(False,"x3")], \
          [(False,"x2"),(True,"x4")] ])
>>> print( c.dimacs(False) )
p cnf 4 2
1 2 -3 0
-2 4 0

You can add clauses later in the process:

>>> c.add_clause( [(False,"x3"),(True,"x4"),(False,"x5")] )
>>> print( c.dimacs(add_header=False))
p cnf 5 3
1 2 -3 0
-2 4 0
-3 4 -5 0

"""

import sys

from itertools import combinations

# Python 2.6 does not have argparse library
try:
    import argparse
except ImportError:
    print("Sorry: %s requires `argparse` library, which is missing.\n"%argv[0],file=sys.stderr)
    print("Either use Python 2.7 or install it from one of the following URLs:",file=sys.stderr)
    print(" * http://pypi.python.org/pypi/argparse",file=sys.stderr)
    print(" * http://code.google.com/p/argparse",file=sys.stderr)
    print("",file=sys.stderr)
    exit(-1)

import random

try:
    import networkx
    import networkx.algorithms
except ImportError:
    print("ERROR: Missing 'networkx' library: no support for graph based formulas.",file=sys.stderr)
    exit(-1)

#################################################################
#          Command line tool follows
#################################################################


class HelpTransformAction(argparse.Action):
    def __init__(self, **kwargs):
        super(HelpTransformAction, self).__init__(**kwargs)

    def __call__(self, parser, namespace, value, option_string=None):
        print("""
        Formula transformations available
        """)
        for k,entry in available_transform().iteritems():
            print("{}\t:  {}".format(k,entry[0]))
        print("\n")
        sys.exit(0)

###
### Command line helpers
###

class _CMDLineHelper(object):
    """Base Command Line helper

    For every formula family there should be a subclass.
    """
    description=None
    name=None

    @staticmethod
    def setup_command_line(parser):
        """Add command line options for this family of formulas
        """
        pass

    @staticmethod
    def additional_options_check(args):
        pass


class _GeneralCommandLine(_CMDLineHelper):
    """Command Line helper for the general commands

    For every formula family there should be a subclass.
    """

    @staticmethod
    def setup_command_line(parser):
        """Setup general command line options

        Arguments:
        - `parser`: parser to fill with options
        """
        parser.add_argument('--output','-o',
                            type=argparse.FileType('wb',0),
                            metavar="<output>",
                            default='-',
                            help="""Output file. The formula is saved
                            on file instead of being sent to standard
                            output. Setting '<output>' to '-' is another
                            way to send the formula to standard output.
                            (default: -)
                            """)
        parser.add_argument('--output-format','-of',
                            choices=['latex','dimacs'],
                            default='dimacs',
                            help="""
                            Output format of the formulas. 'latex' is
                            convenient to insert formulas into papers, and
                            'dimacs' is the format used by sat solvers.
                            (default: dimacs)
                            """)

        parser.add_argument('--seed','-S',
                            metavar="<seed>",
                            default=None,
                            type=str,
                            action='store',
                            help="""Seed for any random process in the
                            program. Any python hashable object will
                            be fine.  (default: current time)
                            """)
        g=parser.add_mutually_exclusive_group()
        g.add_argument('--verbose', '-v',action='store_true',default=True,
                       help="""Output formula header and comments.""")
        g.add_argument('--quiet', '-q',action='store_false',dest='verbose',
                       help="""Output just the formula with no header.""")
        parser.add_argument('--Transform','-T',
                            metavar="<transformation method>",
                            choices=available_transform().keys(),
                            default='none',
                            help="""
                            Transform the CNF formula to make it harder.
                            See `--help-transform` for more information
                            """)
        parser.add_argument('--Tarity','-Ta',
                            metavar="<transformation arity>",
                            type=int,
                            default=None,
                            help="""
                            Hardness parameter for the transformation procedure.
                            See `--help-transform` for more informations
                            """)
        parser.add_argument('--help-transform',nargs=0,action=HelpTransformAction,help="""
                             Formula can be made harder applying some
                             so called "transformation procedures".
                             This gives information about the implemented transformation.
                             """)


### Graph readers/generators

class _GraphHelper(object):
    """Command Line helper for reading graphs
    """

    @staticmethod
    def obtain_graph(args):
        raise NotImplementedError("Graph Input helper must be subclassed")


class _DAGHelper(_GraphHelper,_CMDLineHelper):

    @staticmethod
    def setup_command_line(parser):
        """Setup input options for command lines
        """

        gr=parser.add_argument_group("Reading a directed acyclic graph (DAG) from input")
        gr.add_argument('--input','-i',
                        type=argparse.FileType('r',0),
                        metavar="<input>",
                        default='-',
                        help="""Input file. The DAG is read from a file instead of being read from
                        standard output. Setting '<input>' to '-' is
                        another way to read from standard
                        input.  (default: -)
                        """)
        gr.add_argument('--savegraph','-sg',
                            type=argparse.FileType('wb',0),
                            metavar="<graph_file>",
                            default=None,
                            help="""Output the DAG to a file. The
                            graph is saved, which is useful if the
                            graph is generated internally.
                            Setting '<graph_file>' to '-' is
                            another way to send the graph to
                            standard output.  (default:  -)
                            """)
        gr.add_argument('--graphformat','-gf',
                        choices=graph_formats()['dag'],
                        default=graph_formats()['dag'][0],
                        help="""
                        Format of the DAG in input/output, several
                        formats are supported if networkx is
                        installed.  (default:  {})
                        """.format(graph_formats()['dag'][0]))

        gr=parser.add_argument_group("Generate input DAG from a library")
        gr=gr.add_mutually_exclusive_group()
        gr.add_argument('--tree',type=int,action='store',metavar="<height>",
                            help="tree graph")

        gr.add_argument('--pyramid',type=int,action='store',metavar="<height>",
                            help="pyramid graph")

    @staticmethod
    def obtain_graph(args):
        """Produce a DAG from either input or library
        """
        if hasattr(args,'tree') and args.tree>0:

            D=networkx.DiGraph()
            D.ordered_vertices=[]
            # vertices
            vert=['v_{}'.format(i) for i in range(1,2*(2**args.tree))]
            for w in vert:
                D.add_node(w)
                D.ordered_vertices.append(w)
            # edges
            N=len(vert)-1
            for i in range(len(vert)//2):
                D.add_edge(vert[N-2*i-1],vert[N-i])
                D.add_edge(vert[N-2*i-2],vert[N-i])

        elif hasattr(args,'pyramid') and args.pyramid>0:

            D=networkx.DiGraph()
            D.name='Pyramid of height {}'.format(args.pyramid)
            D.ordered_vertices=[]

            # vertices
            X=[
                [('x_{{{},{}}}'.format(h,i),h,i) for i in range(args.pyramid-h+1)]
                for h in range(args.pyramid+1)
              ]

            for layer in X:
                for (name,h,i) in layer:
                    D.add_node(name,rank=(h,i))
                    D.ordered_vertices.append(name)

            # edges
            for h in range(1,len(X)):
                for i in range(len(X[h])):
                    D.add_edge(X[h-1][i][0]  ,X[h][i][0])
                    D.add_edge(X[h-1][i+1][0],X[h][i][0])

        elif args.graphformat:

            D=readDigraph(args.input,args.graphformat)

        else:
            raise RuntimeError("Invalid graph specification on command line")

        # Output the graph is requested
        if hasattr(args,'savegraph') and args.savegraph:
            writeGraph(D,
                       args.savegraph,
                       args.graphformat,
                       graph_type='dag')

        return D


class _SimpleGraphHelper(_GraphHelper,_CMDLineHelper):

    @staticmethod
    def setup_command_line(parser):
        """Setup input options for command lines
        """

        gr=parser.add_argument_group("Read/Write the underlying undirected graph")
        gr.add_argument('--input','-i',
                        type=argparse.FileType('r',0),
                        metavar="<input>",
                        default='-',
                        help="""Input file. The graph is read from a file instead of being read from
                        standard output. Setting '<input>' to '-' is
                        another way to read from standard
                        input.  (default: -)
                        """)
        gr.add_argument('--savegraph','-sg',
                            type=argparse.FileType('wb',0),
                            metavar="<graph_file>",
                            default=None,
                            help="""Output the graph to a file. The
                            graph is saved, which is useful if the
                            graph is randomly generated internally.
                            Setting '<graph_file>' to '-' is
                            another way to send the graph to
                            standard output.  (default:  -)
                            """)
        gr.add_argument('--graphformat','-gf',
                        choices=graph_formats()['simple'],
                        default=graph_formats()['simple'][0],
                        help="""
                        Format of the graph in input/output, several
                        formats are supported if networkx is
                        installed.  (default:  {})
                        """.format(graph_formats()['simple'][0]))


        gr=parser.add_argument_group("Generate input graph from a library")
        gr=gr.add_mutually_exclusive_group()

        class IntFloat(argparse.Action):
            def __call__(self, parser, args, values, option_string = None):
                n, p = int(values[0]),float(values[1])
                if not isinstance(n,int):
                    raise ValueError('n must be an integer')
                if not (isinstance(p,float) and p<=1.0 and p>=0):
                    raise ValueError('p must be an float between 0 and 1')
                setattr(args, self.dest, (n,p))

        gr.add_argument('--gnp',nargs=2,action=IntFloat,metavar=('n','p'),
                            help="random graph according to G(n,p) model (i.e. independent edges)")


        gr.add_argument('--gnm',type=int,nargs=2,action='store',metavar=('n','m'),
                            help="random graph according to G(n,m) model (i.e. m random edges)")

        gr.add_argument('--gnd',type=int,nargs=2,action='store',metavar=('n','d'),
                            help="random d-regular graph according to G(n,d) model (i.e. d random edges per vertex)")

        gr.add_argument('--grid',type=int,nargs='+',action='store',metavar=('d1','d2'),
                        help="n-dimensional grid of dimension d1 x d2 x ... ")

        gr.add_argument('--torus',type=int,nargs='+',action='store',metavar=('d1','d2'),
                        help="n-dimensional torus grid of dimensions d1 x d2 x ... x dn")

        gr.add_argument('--complete',type=int,action='store',metavar="<N>",
                            help="complete graph on N vertices")

        gr=parser.add_argument_group("Graph modifications")
        gr.add_argument('--plantclique',type=int,action='store',metavar="<k>",
                            help="choose k vertices at random and add all edges among them")


    @staticmethod
    def obtain_graph(args):
        """Build a Graph according to command line arguments

        Arguments:
        - `args`: command line options
        """
        if hasattr(args,'gnd') and args.gnd:

            n,d = args.gnd
            if (n*d)%2 == 1:
                raise ValueError("n * d must be even")
            G=networkx.random_regular_graph(d,n)
            return G

        elif hasattr(args,'gnp') and args.gnp:

            n,p = args.gnp
            G=networkx.gnp_random_graph(n,p)

        elif hasattr(args,'gnm') and args.gnm:

            n,m = args.gnm
            G=networkx.gnm_random_graph(n,m)

        elif hasattr(args,'grid') and args.grid:

            G=networkx.grid_graph(args.grid)

        elif hasattr(args,'torus') and args.torus:
            
            G=networkx.grid_graph(args.torus,periodic=True)

        elif hasattr(args,'complete') and args.complete>0:

            G=networkx.complete_graph(args.complete)

        elif args.graphformat:

            G=readGraph(args.input,args.graphformat)
        else:
            raise RuntimeError("Invalid graph specification on command line")

        # Graph modifications
        if hasattr(args,'plantclique') and args.plantclique>1:

            clique=random.sample(G.nodes(),args.plantclique)

            for v,w in combinations(clique,2):
                G.add_edge(v,w)

        # Output the graph is requested
        if hasattr(args,'savegraph') and args.savegraph:
            writeGraph(G,
                       args.savegraph,
                       args.graphformat,
                       graph_type='simple')

        return G


class _BipartiteGraphHelper(_GraphHelper,_CMDLineHelper):

    @staticmethod
    def setup_command_line(parser):
        """Setup input options for command lines
        """

        # gr=parser.add_argument_group("Read/Write the underlying bipartite graph")
        # gr.add_argument('--input','-i',
        #                 type=argparse.FileType('r',0),
        #                 metavar="<input>",
        #                 default='-',
        #                 help="""Input file. The graph is read from a file instead of being read from
        #                 standard output. Setting '<input>' to '-' is
        #                 another way to read from standard
        #                 input.  (default: -)
        #                 """)
        gr.add_argument('--savegraph','-sg',
                            type=argparse.FileType('wb',0),
                            metavar="<graph_file>",
                            default=None,
                            help="""Output the graph to a file. The
                            graph is saved, which is useful if the
                            graph is randomly generated internally.
                            Setting '<graph_file>' to '-' is
                            another way to send the graph to
                            standard output.  (default:  -)
                            """)
        gr.add_argument('--graphformat','-gf',
                        choices=graph_formats()['simple'],
                        default=graph_formats()['simple'][0],
                        help="""
                        Format of the graph in input/output, several
                        formats are supported if networkx is
                        installed.  (default:  {})
                        """.format(graph_formats()['simple'][0]))


        gr=parser.add_argument_group("Generate input graph from a library")
        gr=gr.add_mutually_exclusive_group()

        class IntIntFloat(argparse.Action):
            def __call__(self, parser, args, values, option_string = None):
                l,r,p = int(values[0]),int(values[1]),float(values[2])
                if not isinstance(l,int):
                    raise ValueError('l must be an integer')
                if not isinstance(r,int):
                    raise ValueError('r must be an integer')
                if not (isinstance(p,float) and p<=1.0 and p>=0):
                    raise ValueError('p must be an float between 0 and 1')
                setattr(args, self.dest, (l,r,p))

        class BipartiteRegular(argparse.Action):
            def __call__(self, parser, args, values, option_string = None):
                l,r,d = int(values[0]),int(values[1]),int(values[2])
                if not isinstance(l,int):
                    raise ValueError('l must be an integer')
                if not isinstance(r,int):
                    raise ValueError('r must be an integer')
                if not isinstance(d,int):
                    raise ValueError('d must be an integer')
                if (d*l % r) != 0 :
                    raise ValueError('In a regular bipartite graph, r must divide d*l.')
                setattr(args, self.dest, (l,r,p))

        # gr.add_argument('--bp',nargs=2,action=IntFloat,metavar=('l','r','p'),
        #         help="random bipartite graph according with independent edges)")


        # gr.add_argument('--bm',type=int,nargs=2,action='store',metavar=('l','r','m'),
        #         help="random bipartite graph, with m random edges")

        # gr.add_argument('--bleftd',type=int,nargs=2,action='store',metavar=('l','r','d'),
        #         help="random bipartite d-left-regular graph, with d random edges per left vertex)")

        # gr.add_argument('--bregular',type=int,nargs=3,action='store',metavar=('l','r','d'),
        #         help="random (l,r)-bipartite regular graph, with d edges per left vertex.")

        # gr.add_argument('--bcomplete',type=int,nargs=2,action='store',metavar=('l','r'),
        #         help="complete bipartite graph")

        # gr=parser.add_argument_group("Graph modifications")
        # gr.add_argument('--plantclique',type=int,action='store',metavar="<k>",
        #                     help="choose k vertices per side and add all edges among them")


    @staticmethod
    def obtain_graph(args):
        """Build a Bipartite graph according to command line arguments

        Arguments:
        - `args`: command line options
        """
        if hasattr(args,'bp') and args.bp:

            raise ValueError("Not implenented")

        elif hasattr(args,'bm') and args.bm:

            raise ValueError("Not implenented")

        elif hasattr(args,'bleftd') and args.bleftd:

            raise ValueError("Not implenented")

        elif hasattr(args,'bregular') and args.bregular:

            raise ValueError("Not implenented")

        elif hasattr(args,'bcomplete') and args.torus:
            
            raise ValueError("Not implenented")

        else:
            raise RuntimeError("Invalid graph specification on command line")

        # Graph modifications
        if hasattr(args,'plantclique') and args.plantclique>1:

            raise ValueError("Not implenented")

        # Output the graph is requested
        if hasattr(args,'savegraph') and args.savegraph:
            writeGraph(G,
                       args.savegraph,
                       args.graphformat,
                       graph_type='bipartite')

        return G


### Formula families

class _FormulaFamilyHelper(object):
    """Command Line helper for formula families

    For every formula family there should be a subclass.
    """
    description=None
    name=None

    @staticmethod
    def build_cnf(args):
        pass


class _PHP(_FormulaFamilyHelper,_CMDLineHelper):
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
        parser.set_defaults(func=_PHP.build_cnf)

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


class _RAM(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for RamseyNumber formulas
    """
    name='ram'
    description='ramsey number principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Ramsey formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('s',metavar='<s>',type=int,help="Forbidden independent set size")
        parser.add_argument('k',metavar='<k>',type=int,help="Forbidden independent clique")
        parser.add_argument('N',metavar='<N>',type=int,help="Graph size")

    @staticmethod
    def build_cnf(args):
        """Build a Ramsey formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return RamseyNumber(args.s, args.k, args.N)


class _OP(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for Ordering principle formulas
    """
    name='op'
    description='ordering principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Ordering principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('N',metavar='<N>',type=int,help="domain size")
        g=parser.add_mutually_exclusive_group()
        g.add_argument('--total','-t',default=False,action='store_true',help="assume a total order")
        g.add_argument('--smart','-s',default=False,action='store_true',help="encode 'x<y' and 'x>y' in a single variable (implies totality)")
        g.add_argument('--knuth2', action='store_const', dest='knuth',const=2,
                       help="transitivity axioms: \"(i<j)(j<k)->(i,k)\" only for j>i,k")
        g.add_argument('--knuth3', action='store_const', dest='knuth',const=3,
                       help="transitivity axioms: \"(i<j)(j<k)->(i,k)\" only for k>i,j")
        parser.add_argument('--plant','-p',default=False,action='store_true',help="allow a minimum element")

    @staticmethod
    def build_cnf(args):
        """Build an Ordering principle formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        return OrderingPrinciple(args.N,args.total,args.smart,args.plant,args.knuth)


class _GOP(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for Graph Ordering principle formulas
    """
    name='gop'
    description='graph ordering principle'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Graph ordering principle formula

        Arguments:
        - `parser`: parser to load with options.
        """
        g=parser.add_mutually_exclusive_group()
        g.add_argument('--total','-t',default=False,action='store_true',help="assume a total order")
        g.add_argument('--smart','-s',default=False,action='store_true',help="encode 'x<y' and 'x>y' in a single variable (implies totality)")
        g.add_argument('--knuth2', action='store_const', dest='knuth',const=2,
                       help="transitivity axioms: \"(i<j)(j<k)->(i,k)\" only for j>i,k")
        g.add_argument('--knuth3', action='store_const', dest='knuth',const=3,
                       help="transitivity axioms: \"(i<j)(j<k)->(i,k)\" only for k>i,j")
        parser.add_argument('--plant','-p',default=False,action='store_true',help="allow a minimum element")
        _SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build a Graph ordering principle formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G=_SimpleGraphHelper.obtain_graph(args)
        return GraphOrderingPrinciple(G,args.total,args.smart,args.plant,args.knuth)


class _KClique(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for k-clique formula
    """
    name='kclique'
    description='k clique formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for k-clique formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('k',metavar='<k>',type=int,action='store',help="size of the clique to be found")
        _SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build a k-clique formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G=_SimpleGraphHelper.obtain_graph(args)
        return SubgraphFormula(G,[networkx.complete_graph(args.k)])


class _KColor(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for k-color formula
    """
    name='kcolor'
    description='k-colorability formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for k-color formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('k',metavar='<k>',type=int,action='store',help="number of available colors")
        _SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build a k-colorability formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G=_SimpleGraphHelper.obtain_graph(args)
        return ColoringFormula(G,range(1,args.k+1))


class _RAMLB(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for ramsey graph formula
    """
    name='ramlb'
    description='unsat if G witnesses that r(k,s)>|V(G)| (i.e. G has not k-clique nor s-stable)'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for ramsey witness formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('k',metavar='<k>',type=int,action='store',help="size of the clique to be found")
        parser.add_argument('s',metavar='<s>',type=int,action='store',help="size of the stable to be found")
        _SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build a formula to check that a graph is a ramsey number lower bound

        Arguments:
        - `args`: command line options
        """
        G=_SimpleGraphHelper.obtain_graph(args)
        return SubgraphFormula(G,[networkx.complete_graph(args.k),
                                  networkx.complete_graph(args.s)])



class _TSE(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for Tseitin  formulas
    """
    name='tseitin'
    description='tseitin formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for Tseitin formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('--charge',metavar='<charge>',default='first',
                            choices=['first','random','randomodd','randomeven'],
                            help="""charge on the vertices.
                                    `first'  puts odd charge on first vertex;
                                    `random' puts a random charge on vertices;
                                    `randomodd' puts random odd  charge on vertices;
                                    `randomeven' puts random even charge on vertices.
                                     """)
        _SimpleGraphHelper.setup_command_line(parser)

    @staticmethod
    def build_cnf(args):
        """Build Tseitin formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        G=_SimpleGraphHelper.obtain_graph(args)

        if G.order()<1:
            charge=None

        elif args.charge=='first':

            charge=[1]+[0]*(G.order()-1)

        else: # random vector
            charge=[random.randint(0,1) for i in xrange(G.order()-1)]

            parity=sum(charge) % 2

            if args.charge=='random':
                charge.append(random.randint(0,1))
            elif args.charge=='randomodd':
                charge.append(1-parity)
            elif args.charge=='randomeven':
                charge.append(parity)
            else:
                raise ValueError('Illegal charge specification on command line')

        return TseitinFormula(G,charge)


class _OR(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for a single clause formula
    """
    name='or'
    description='a single disjunction'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for single or of literals

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('P',metavar='<P>',type=int,help="positive literals")
        parser.add_argument('N',metavar='<N>',type=int,help="negative literals")


    @staticmethod
    def build_cnf(args):
        """Build an disjunction

        Arguments:
        - `args`: command line options
        """
        clause = [ (True,"x_{}".format(i)) for i in range(args.P) ] + \
                 [ (False,"y_{}".format(i)) for i in range(args.N) ]
        return CNF([clause],
                   header="""Single clause with {} positive and {} negative literals""".format(args.P,args.N))


class _PEB(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for a single clause formula
    """
    name='peb'
    description='pebbling formula'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for pebbling formulas

        Arguments:
        - `parser`: parser to load with options.
        """
        _DAGHelper.setup_command_line(parser)

    @staticmethod
    def build_cnf(args):
        """Build the pebbling formula

        Arguments:
        - `args`: command line options
        """
        D=_DAGHelper.obtain_graph(args)
        try:
            return PebblingFormula(D)
        except RuntimeError:
            print("\nError: input graph must be directed and acyclic.",file=sys.stderr)
            sys.exit(-1)
            
class _AND(_FormulaFamilyHelper,_CMDLineHelper):
    """Command line helper for a single clause formula
    """
    name='and'
    description='a single conjunction'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for an and of literals

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('P',metavar='<P>',type=int,help="positive literals")
        parser.add_argument('N',metavar='<N>',type=int,help="negative literals")


    @staticmethod
    def build_cnf(args):
        """Build a conjunction

        Arguments:
        - `args`: command line options
        """
        clauses = [ [(True,"x_{}".format(i))] for i in range(args.P) ] + \
                  [ [(False,"y_{}".format(i))] for i in range(args.N) ]
        return CNF(clauses,
                   header="""Singleton clauses: {} positive and {} negative""".format(args.P,args.N))


###
### Register signals
###
import signal
def signal_handler(insignal, frame):
    print('Program interrupted',file=sys.stderr)
    sys.exit(-1)

signal.signal(signal.SIGINT, signal_handler)

###
### Main program
###
def command_line_utility(argv=sys.argv):

    # Commands and subcommand lines
    cmdline = _GeneralCommandLine
    subcommands=[_PHP,_TSE,_OP,_GOP,_PEB,_RAM,_RAMLB,_KClique,_KColor,_OR,_AND]

    # Parse the command line arguments
    parser=argparse.ArgumentParser(prog='cnfgen',epilog="""
    Each <formula type> has its own command line arguments and options.
    For more information type 'cnfgen <formula type> [--help | -h ]'
    """)
    cmdline.setup_command_line(parser)
    subparsers=parser.add_subparsers(title="Available formula types",metavar='<formula type>')

    # Setup of various formula command lines options
    for sc in subcommands:
        p=subparsers.add_parser(sc.name,help=sc.description)
        sc.setup_command_line(p)
        p.set_defaults(subcommand=sc)

    # Process the options
    args=parser.parse_args(argv[1:])
    cmdline.additional_options_check(args)
    args.subcommand.additional_options_check(args)

    # If necessary, init the random generator
    if hasattr(args,'seed') and args.seed:
        random.seed(args.seed)

    # Generate the basic formula
    cnf=args.subcommand.build_cnf(args)

    # Apply a formula transformation
    tcnf=TransformFormula(cnf,args.Transform,args.Tarity)


    # Do we wnat comments or not

    if args.output_format == 'latex':
        output = tcnf.latex()

    elif args.output_format == 'dimacs':
        output = tcnf.dimacs(export_header=args.verbose)
    else:
        output = tcnf.dimacs(export_header=args.verbose)

    print(output,file=args.output)

    if args.output!=sys.stdout:
        args.output.close()


### Launcher
if __name__ == '__main__':
    command_line_utility(sys.argv)
