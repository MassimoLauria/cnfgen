
Graph based formulas
====================

The  structure  of  many  formulas included  in  ``CNFgen``  is  based
on  graph, e.g.  a  formula that  claims that  a  bipartite graph  has
a perfect  matching, or that  a certain simple  graph has a  clique of
a  certain size.  There  are four  different types  of  graph used  in
``CNFgen``.

  + ``simple`` (simple graph): standard undirected simple graphs.
  + ``bipartite``  (bipartite graphs):  vertices  are  divided in  two
    classes and there are no edges between vertices of the same class.
  + ``digraph`` (directed graph): each edge of these graphs have an orientation.
  + ``dag`` (directed acyclic graph):  directed graphs with no cycles,
    they induce partial orderings.

