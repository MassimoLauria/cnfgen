   
Formula families
================

One of the most useful features of ``CNFgen`` is the implementation of
several important families of CNF formulas, many of them either coming
from  the  proof  complexity  literature or  encoding  some  important
problem  from combinatorics.  The formula  are accessible  through the
:py:mod:`cnfformula` package. See for example this construction of the
pigeohole principle formula with 10 pigeons and 9 holes.

   >>> import cnfformula
   >>> F = cnfformula.PigeonholePrinciple(10,9)
   >>> F.is_satisfiable()
   (False, None)


Included formula families
--------------------------
.. unfortunately this list cannot be generated automatically.

All formula  generators are  accessible from  the :py:mod:`cnfformula`
package, but their implementation  (and documentation) is split across
the following modules. This makes it easy to
`add new formula families. <addfamily.html>`_
   
.. toctree::
   :titlesonly:

   Counting formulas <cnfformula.families.counting>
   Graph coloring <cnfformula.families.coloring>
   Graph Isomorphism <cnfformula.families.graphisomorphism>
   Ordering principles <cnfformula.families.ordering>
   Pebbling formulas <cnfformula.families.pebbling>
   Pigeonhole principle <cnfformula.families.pigeonhole>
   Ramsey numbers <cnfformula.families.ramsey>
   Random CNFs <cnfformula.families.randomformulas>
   Clique and Subgraph formulas <cnfformula.families.subgraph>
   Subset Cardinality <cnfformula.families.subsetcardinality>
   Tseitin formula <cnfformula.families.tseitin>
   Basic formulas <cnfformula.families.simple>


Command line invocation
-----------------------
Furthermore it is possible to  generate the formulas directly from the
command line. To list all formula families accessible from the command
line just run the command ``cnfgen --help``. To get information about
the specific command  line parameters for a formula  generator run the
command ``cnfgen <generator_name> --help``.

Recall the  example above, in  hich we produced a  pigeohole principle
formula for 10  pigeons and 9 holes.  We can get the  same formula in
DIMACS format with the following command line.
   
.. code-block:: shell

   $ cnfgen php 10 9
   c Pigeonhole principle formula for 10 pigeons and 9 holes
   c Generated with `cnfgen` (C) 2012-2016 Massimo Lauria <lauria.massimo@gmail.com>
   c https://massimolauria.github.io/cnfgen
   c
   p cnf 90 415
   1 2 3 4 5 6 7 8 9 0
   10 11 12 13 14 15 16 17 18 0
   19 20 21 22 23 24 25 26 27 0
   28 29 30 31 32 33 34 35 36 0
   37 38 39 40 41 42 43 44 45 0
   46 47 48 49 50 51 52 53 54 0
   55 56 57 58 59 60 61 62 63 0
   64 65 66 67 68 69 70 71 72 0
   73 74 75 76 77 78 79 80 81 0
   82 83 84 85 86 87 88 89 90 0
   -1 -10 0
   -1 -19 0
   -1 -28 0
   -1 -37 0
   -1 -46 0
   -1 -55 0
   -1 -64 0
   -1 -73 0
   -1 -82 0
   -10 -19 0
   -10 -28 0
   -10 -37 0
   -10 -46 0
   ...
   -72 -81 0
   -72 -90 0
   -81 -90 0
                
