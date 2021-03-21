   
Formula families
================

The defining features  of ``CNFgen`` is the  implementation of several
important families  of CNF formulas,  many of them either  coming from
the  proof complexity  literature or  encoding some  important problem
from   combinatorics.  The   formula   are   accessible  through   the
:py:mod:`cnfgen`  package. See  for example  this construction  of the
pigeohole principle formula with 5 pigeons and 4 holes.

   >>> import cnfgen
   >>> F = cnfgen.PigeonholePrinciple(5,4)
   >>> F.is_satisfiable()
   False


Included formula families
--------------------------
.. unfortunately this list cannot be generated automatically.

All formula  generators are  accessible from  the :py:mod:`cnfformula`
package, but their implementation  (and documentation) is split across
the following modules. This makes it easy to
`add new formula families. <addfamily.html>`_
   
.. toctree::
   :titlesonly:

   Counting formulas <cnfgen.families.counting>
   Graph coloring <cnfgen.families.coloring>
   Graph Isomorphism <cnfgen.families.graphisomorphism>
   Ordering principles <cnfgen.families.ordering>
   Pebbling formulas <cnfgen.families.pebbling>
   Pigeonhole principle <cnfgen.families.pigeonhole>
   Pitfall formulas <cnfgen.families.pitfall>
   Ramsey numbers <cnfgen.families.ramsey>
   Random CNFs <cnfgen.families.randomformulas>
   Clique and Subgraph formulas <cnfgen.families.subgraph>
   Subset Cardinality <cnfgen.families.subsetcardinality>
   Clique-Coloring formulas <cnfgen.families.cliquecoloring>
   Tseitin formula <cnfgen.families.tseitin>
   Coloured Polynomial Local Search <cnfgen.families.cpls>


Command line invocation
-----------------------
Furthermore it is possible to  generate the formulas directly from the
command line. To list all formula families accessible from the command
line just run the command ``cnfgen --help``. To get information about
the specific command  line parameters for a formula  generator run the
command ``cnfgen <generator_name> --help``.

Recall the  example above, in  hich we produced a  pigeohole principle
formula for 5  pigeons and 4 holes.  We can get the  same formula in
DIMACS format with the following command line.
   
.. code-block:: shell

   $ cnfgen php 5 4
   c description: Pigeonhole principle formula for 5 pigeons and 4 holes
   c generator: CNFgen (0.8.6-5-g56a1e50)
   c copyright: (C) 2012-2020 Massimo Lauria <massimo.lauria@uniroma1.it>
   c url: https://massimolauria.net/cnfgen
   c command line: cnfgen php 5 4
   c
   p cnf 20 45
   1 2 3 4 0
   5 6 7 8 0
   9 10 11 12 0
   13 14 15 16 0
   17 18 19 20 0
   -1 -5 0
   -1 -9 0
   -1 -13 0
   -1 -17 0
   -5 -9 0
   -5 -13 0
   -5 -17 0
   -9 -13 0
   -9 -17 0
   -13 -17 0
   -2 -6 0
   -2 -10 0
   -2 -14 0
   -2 -18 0
   -6 -10 0
   -6 -14 0
   -6 -18 0
   -10 -14 0
   -10 -18 0
   -14 -18 0
   -3 -7 0
   -3 -11 0
   -3 -15 0
   -3 -19 0
   -7 -11 0
   -7 -15 0
   -7 -19 0
   -11 -15 0
   -11 -19 0
   -15 -19 0
   -4 -8 0
   -4 -12 0
   -4 -16 0
   -4 -20 0
   -8 -12 0
   -8 -16 0
   -8 -20 0
   -12 -16 0
   -12 -20 0
   -16 -20 0
