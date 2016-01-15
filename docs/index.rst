.. Entry point document of CNFgen library documentation
   
.. toctree::
   :caption: Table of contents
   :hidden:
   :maxdepth: 2
   :numbered:

   self
   buildcnf
   satsolve
   families
   graphs
   transform
   cnfgen
   addfamily
   

Welcome to CNFgen's documentation!
==================================

The main components of CNFgen are the ``cnfformula`` library and
the ``cnfgen`` command line utility.

The ``cnfformula`` library
--------------------------

The ``cnfformula``  library is capable to  generate Conjunctive Normal
Form   (CNF)   formulas,   manipulate   them  and,   when   there   is
a satisfiability (SAT) solver properly  installed on your system, test
their satisfiability. The CNFs can be  saved on file in DIMACS format,
which the standard input format for  SAT solvers [1]_, or converted to
LaTeX [2]_  to be included  in a  document. The library  contains many
generators for formulas that  encode various combinatorial problems or
that come from research in Proof Complexity [3]_.

The  main  entry point  for  the  library is  the  :py:class:`cnfformula.CNF`
object. Let's see a simple example of its usage.

   >>> import cnfformula
   >>> F = cnfformula.CNF()
   >>> F.add_clause([(True,"X"),(False,"Y")])
   >>> F.add_clause([(False,"X")])
   >>> F.is_satisfiable()
   (True, {'Y':False, 'X':False})
   >>> F.add_clause([(True,"Y")])
   >>> F.is_satisfiable()
   (False, None)
   >>> print F.dimacs()
   c Generated with `cnfgen` (C) 2012-2016 Massimo Lauria <lauria.massimo@gmail.com>
   c https://github.com/MassimoLauria/cnfgen.git
   c
   p cnf 2 3
   1 -2 0
   -1 0
   2 0
   >>> print F.latex()
   % Generated with `cnfgen` (C) 2012-2016 Massimo Lauria <lauria.massimo@gmail.com>
   % https://github.com/MassimoLauria/cnfgen.git
   %
   \begin{align}
   &       \left(     {X} \lor \neg{Y} \right) \\
   & \land \left( \neg{X} \right) \\
   & \land \left(     {Y} \right)
   \end{align}

A typical  unsatisfiable formula  studied in  Proof Complexity  is the
pigeonhole principle formula.

   >>> from cnfformula import PigeonholePrinciple
   >>> F = PigeonholePrinciple(5,4)
   >>> print F.dimacs()
   c Pigeonhole principle formula for 5 pigeons and 4 holes
   c Generated with `cnfgen` (C) 2012-2016 Massimo Lauria <lauria.massimo@gmail.com>
   c https://github.com/MassimoLauria/cnfgen.git
   c
   p cnf 20 45
   1 2 3 4 0
   5 6 7 8 0
   ...
   -16 -20 0
   >>> F.is_satisfiable()
   (False, None)

The ``cnfgen`` command line tool
--------------------------------

The command line  tool is installed along  ``cnfformula`` package, and
provides  a somehow  limited  interface to  the library  capabilities.
It provides ways  to produce formulas in DIMACS and  LaTeX format from
the command line. To produce a  pigeonhole principle from 5 pigeons to
4 holes as in the previous example the command line is

.. code-block:: shell
                
   $ cnfgen php 5 4
   c Pigeonhole principle formula for 5 pigeons and 4 holes
   c Generated with `cnfgen` (C) Massimo Lauria <lauria.massimo@gmail.com>
   c https://github.com/MassimoLauria/cnfgen.git
   c
   p cnf 20 45
   1 2 3 4 0
   5 6 7 8 0
   ...
   -16 -20 0
   
For a documentation on how to use ``cnfgen`` command please type
``cnfgen  --help``  and for  further  documentation  about a  specific
formula generator type ``cnfgen <generator_name> --help``.

Reference
---------
.. [1] http://www.satlib.org/Benchmarks/SAT/satformat.ps
.. [2] http://www.latex-project.org/ 
.. [3] http://en.wikipedia.org/wiki/Proof_complexity

       
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

