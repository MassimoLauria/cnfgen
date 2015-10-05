
Graph based formulas
====================

The  structure of  many formulas  included in  ``CNFgen`` is  based on
graphs. We use four different types of graphs in our formula families.

  + ``simple`` (simple graph): standard undirected simple graphs.
  + ``bipartite``  (bipartite graphs):  vertices  are  divided in  two
    classes and there are no edges between vertices of the same class.
  + ``digraph`` (directed graph): each edge of these graphs have an orientation.
  + ``dag`` (directed acyclic graph):  directed graphs with no cycles,
    they induce partial orderings.

Most of the code manipulating graphs is due to the NetworkX_, which is
used behind the  scene to generate particular graphs, and  to read and
write    graphs   in    standard    file    formats.   The    function
:py:func:`cnfformula.graphs.supported_formats`  lists the  file formats
available for each graph type.

   >>> from cnfformula.graphs import supported_formats
   >>> supported_formats()
   {'bipartite': ['matrix', 'gml', 'dot'],
    'dag': ['adjlist', 'gml', 'dot'],
    'digraph': ['adjlist', 'gml', 'dot', 'dimacs'],
    'simple': ['adjlist', 'gml', 'dot', 'dimacs']}

The ``dot`` format  is from Graphviz_ and it is  available only if the
optional ``pygraphviz`` package is installed  in the system. The Graph
Modelling Language  (GML_) ``gml``  is the  current standard  in graph
representation. The DIMACS_ (``dimacs``) format [#]_ is sometimes used
for programming  competitions or  in the theoretical  computer science
community.  The ``adjlist``  and  ``matrix`` formats  are defined  and
implemented inside ``CNFgen``.

.. note::

   More information about  the supported graph file formats  is in the
   `User  Documentation`_   for  the  ``cnfgen``  command   line  too.
   In   particular  there   is  a   description  of   ``adjlist``  and
   ``matrix`` formats.


Graph I/O
---------

.. _`User Documentation`: http://massimolauria.github.io/cnfgen/graphformats.html
.. _cnfgengraph: http://massimolauria.github.io/cnfgen/graphformats.html
.. _DIMACS: http://prolland.free.fr/works/research/dsat/dimacs.html
.. _GML: http://www.infosun.fim.uni-passau.de/Graphlet/GML/gml-tr.html
.. _Graphviz: http://www.graphviz.org/content/dot-language
.. _NetworkX: https://networkx.github.io/

.. [#] Here we talk about the DIMACS format for graphs, not the
       one for CNF formulas.
