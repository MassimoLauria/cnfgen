
Graph based formulas
====================

The  most  interesting  benchmark  formulas have  a  graph  structure.
See the following  example, where :py:func:`cnfformula.TseitinFormula`
is realized over a star graph with five arms.


   >>> import cnfformula
   >>> import networkx as nx
   >>> from pprint import pprint
   >>> G = nx.star_graph(5)
   >>> sorted(G.edges())
   [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5)]
   >>> F = cnfformula.TseitinFormula(G,charges=[0,1,1,0,1,1])
   >>> pprint(F.is_satisfiable())
   (True,
    {'E_{0,1}': True,
     'E_{0,2}': True,
     'E_{0,3}': False,
     'E_{0,4}': True,
     'E_{0,5}': True})

Tseitin formulas can  be really hard for if the  graph has large `edge
expansion <https://en.wikipedia.org/wiki/Expander_graph>`_. Indeed the
unsatisfiable  version of  this formula  requires exponential  running
time in any resolution based SAT solver [1]_.
     
In  the  previous example  the  structure  of  the  CNF was  a  simple
undirected graph, but in ``CNFgen`` we have formulas built around four
different types of graphs.

+---------------+------------------------+-------------------------------------------------+
| ``simple``    | simple graph           | default graph                                   |
+---------------+------------------------+-------------------------------------------------+
| ``bipartite`` | bipartite graph        | vertices split in two inpedendent sets          |
+---------------+------------------------+-------------------------------------------------+
| ``digraph``   | directed graph         | each edge has an orientation                    |
+---------------+------------------------+-------------------------------------------------+
| ``dag``       | directed acyclic graph | no cycles, edges induce a partial ordering      |
+---------------+------------------------+-------------------------------------------------+

To manipulate graphs ``CNFgen`` does  not reinvent the wheel, but uses
the famous  NetworkX_ library behind the  scene. ``NetworkX`` supports
reading and writing  graph from/to files, and  ``CNFgen`` leverages on
that.  Furthermore  ``CNFgen``  implements  graph  I/O  in  few  other
file formats. The function
:py:func:`cnfformula.graphs.supported_formats` lists  the file formats
available for each graph type.

   >>> from cnfformula.graphs import supported_formats
   >>> from pprint import pprint
   >>> pprint(supported_formats())
   {'bipartite': ['kthlist', 'matrix', 'gml', 'dot'],
    'dag': ['kthlist', 'gml', 'dot'],
    'digraph': ['kthlist', 'gml', 'dot', 'dimacs'],
    'simple': ['kthlist', 'gml', 'dot', 'dimacs']}

The ``dot`` format  is from Graphviz_ and it is  available only if the
optional  ``pydot``  python  package  is  installed  in  the  system.
The Graph Modelling Language (GML_) ``gml`` is the current standard in
graph  representation. The  DIMACS_ (``dimacs``)  format [2]_  is used
sometimes for programming competitions  or in the theoretical computer
science community. The ``kthlist``  and ``matrix`` formats are defined
and implemented inside ``CNFgen``.

.. note::

   More information about  the supported graph file formats  is in the
   `User  Documentation`_   for  the  ``cnfgen``  command   line  too.
   In   particular  there   is  a   description  of   ``kthlist``  and
   ``matrix`` formats.


Directed Acyclic Graphs and Bipartite Graphs
--------------------------------------------

``NetworkX`` does  not have a  specific data structure for  a directed
acyclic graphs  (DAGs). In  ``CNFgen`` a  DAG is  any object  which is
either           a           :py:class:`networkx.DiGraph`           or
:py:class:`networkx.MultiDiGraph`  instance,   and  which  furthermore
passes the test :py:func:`cnfformula.graphs.is_dag`.

   >>> import networkx as nx
   >>> G = nx.DiGraph()
   >>> nx.add_cycle(G,[1,2,3])
   >>> cnfformula.graphs.is_dag(G)
   False
   >>> H = nx.DiGraph()
   >>> nx.add_path(H,[1,2,3])
   >>> cnfformula.graphs.is_dag(H)
   True
   
In the same way ``NetworkX`` does not have a particular data structure
for    bipartite     graphs    (     :py:class:`networkx.Graph`    and
:py:class:`networkx.MultiGraph` are possible  choices), but it follows
the convention that  all vertices in the graph  have the ``bipartite``
attribute  that  gets values  :math:`\{0,1\}`  [3]_.  The CNF  formula
constructions that make use of  bipartite graphs usually associate the
:math:`0`  part as  the  left  side, and  the  :math:`1`  part to  the
right side.  The function :py:func:`cnfformula.graphs.has_bipartition`
tests whether this bipartition exists in a graph.


   >>> import networkx as nx
   >>> G = nx.bipartite.havel_hakimi_graph([2,1],[1,1,1])
   >>> cnfformula.graphs.has_bipartition(G)
   True
   >>> from pprint import pprint
   >>> pprint(dict(G.nodes()))
   {0: {'bipartite': 0},
    1: {'bipartite': 0},
    2: {'bipartite': 1},
    3: {'bipartite': 1},
    4: {'bipartite': 1}}
   >>> sorted(G.edges())
   [(0, 3), (0, 4), (1, 2)]
   >>> F = cnfformula.GraphPigeonholePrinciple(G)
   >>> sorted(F.variables())
   ['p_{0,3}', 'p_{0,4}', 'p_{1,2}']

   
Graph I/O
---------

The  :py:mod:`cnfformula.graphs`  module  implements  a  graph  reader
:py:mod:`cnfformula.graphs.readGraph`     and    a     graph    writer
:py:mod:`cnfformula.graphs.writeGraph`  to  facilitate  graph  I/O.
..
Both  ``readGraph`` and  ``writeGraph`` operate  either on  filenames,
encoded  as :py:class:`str`  or :py:class:`unicode`,  or otherwise  on
file-like objects such as

   + standard file objects (including :py:obj:`sys.stdin` and :py:obj:`sys.stdout`);
   + string buffers of type :py:class:`StringIO.StringIO`;
   + in-memory text streams that inherit from :py:class:`io.TextIOBase`.
     
   >>> import sys
   >>> from io import BytesIO
   >>> import networkx as nx
   >>> from cnfformula.graphs import readGraph, writeGraph

   >>> G = nx.bipartite.havel_hakimi_graph([2,1],[1,1,1])
   >>> writeGraph(G,sys.stdout,graph_type='bipartite',file_format='gml')
   graph [
     multigraph 1
     name "bipartite_havel_hakimi_graph"
     node [
       id 0
       label "0"
       bipartite 0
     ]
     node [
       id 1
       label "1"
       bipartite 0
     ]
     node [
       id 2
       label "2"
       bipartite 1
     ]
     node [
       id 3
       label "3"
       bipartite 1
     ]
     node [
       id 4
       label "4"
       bipartite 1
     ]
     edge [
       source 0
       target 3
       key 0
     ]
     edge [
       source 0
       target 4
       key 0
     ]
     edge [
       source 1
       target 2
       key 0
     ]
   ]
   <BLANKLINE>
   >>> from io import StringIO
   >>> textbuffer = StringIO("graph X { 1 -- 2 -- 3 }")
   >>> G = readGraph(textbuffer, graph_type='simple', file_format='dot')
   >>> E = G.edges()
   >>> ('1','2') in E
   True
   >>> ('2','3') in E
   True
   >>> ('1','3') in E
   False
   
There are  several advantages with  using those functions,  instead of
the reader/writer  implemented ``NextowrkX``. First of  all the reader
always  verifies that  when reading  a graph  of a  certain type,  the
actual input  actually matches the type.  For example if the  graph is
supposed  to  be  a DAG,  then  :py:func:`cnfformula.graphs.readGraph`
would check that.

   >>> buffer = StringIO('digraph A { 1 -- 2 -- 3 -- 1}')
   >>> readGraph(buffer,graph_type='dag',file_format='dot')
   Traceback (most recent call last):
   ...
   ValueError: [Input error] Graph must be acyclic

When the  file object has an  associated file name, it  is possible to
omit the ``file_format`` argument. In this latter case the appropriate
choice of format  will be guessed by the file  extension.

   >>> with open(tmpdir+"example_dag1.dot","w") as f:
   ...     print("digraph A {1->2->3}",file=f)
   >>> G = readGraph(tmpdir+"example_dag1.dot",graph_type='dag')
   >>> sorted(G.edges())
   [('1', '2'), ('2', '3')]

is equivalent to
   
   >>> with open(tmpdir+"example_dag2.gml","w") as f:
   ...     print("digraph A {1->2->3}",file=f)
   >>> G = readGraph(tmpdir+"example_dag2.gml",graph_type='dag',file_format='dot')
   >>> sorted(G.edges())
   [('1', '2'), ('2', '3')]

Instead, if we omit the format and the file extension is misleading we
would get and error.
   
   >>> with open(tmpdir+"example_dag3.gml","w") as f:
   ...     print("digraph A {1->2->3}",file=f)
   >>> G = readGraph(tmpdir+"example_dag3.gml",graph_type='dag')
   Traceback (most recent call last):
   ...
   ValueError: [Parse error in GML input] ...

This is an example of GML file.
   
   >>> gml_text ="""graph [
   ...               node [
   ...                 id 0
   ...                 label "a"
   ...               ]
   ...               node [
   ...                 id 1
   ...                 label "b"
   ...               ]
   ...               edge [
   ...                 source 0
   ...                 target 1
   ...               ]
   ...             ]"""
   >>> with open(tmpdir+"example_ascii.gml","w",encoding='ascii') as f:
   ...     print(gml_text,file=f)
   >>> G = readGraph(tmpdir+"example_ascii.gml",graph_type='simple')
   >>> ('b','a') in G.edges()
   True

Recall that GML files are supposed to be ASCII encoded. 

   >>> gml_text2="""graph [
   ...               node [
   ...                 id 0
   ...                 label "à"
   ...               ]
   ...               node [
   ...                 id 1
   ...                 label "è"
   ...               ]
   ...               edge [
   ...                 source 0
   ...                 target 1
   ...               ]
   ...             ]"""

   >>> with open(tmpdir+"example_utf8.gml","w",encoding='utf-8') as f:
   ...     print(gml_text2,file=f)
   >>> G = readGraph(tmpdir+"example_utf8.gml",graph_type='dag')
   Traceback (most recent call last):
   ...
   ValueError: [Non-ascii chars in GML file] ...

Graph generators
----------------



.. note::

   See  the documentation  of the  module :py:mod:`cnfformula.graphs`
   for more information about the ``CNFgen`` support code for graphs.


.. _`User Documentation`: http://massimolauria.github.io/cnfgen/graphformats.html
.. _cnfgengraph: http://massimolauria.github.io/cnfgen/graphformats.html
.. _DIMACS: http://prolland.free.fr/works/research/dsat/dimacs.html
.. _GML: http://www.infosun.fim.uni-passau.de/Graphlet/GML/gml-tr.html
.. _Graphviz: http://www.graphviz.org/content/dot-language
.. _NetworkX: https://networkx.github.io/


   
References
----------

.. [1] A.  Urquhart. `Hard  examples for  resolution`. Journal  of the
       ACM (1987) http://dx.doi.org/10.1145/48014.48016

.. [2] Beware. Here we are talking about the DIMACS format for graphs, not the
       DIMACS file format for CNF formulas.

.. [3] This convention is describe in 
       http://networkx.readthedocs.org/en/latest/reference/algorithms.bipartite.html

