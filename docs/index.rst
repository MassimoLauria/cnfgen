.. CNFgen documentation master file, created by
   sphinx-quickstart on Tue May 26 17:12:40 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to CNFgen's documentation!
==================================

The main components of this package are the ``cnfformula`` library and
the ``cnfgen`` command line utility.

.. toctree::
   :maxdepth: 2

The ``cnfformula`` library
--------------------------

The ``cnfformula``  library is  capable to generate  CNFs (Conjunctive
Normal Form) formulas, manipulate  them and test their satisfiability,
assuming  there is  a SAT  solver properly  installed on  your system.
The CNFs  can be saved  on file in  DIMACS format, the  standard input
format for SAT solvers [1]_, or output in LaTeX [2]_ to be included in
a document. It also contains  many generators for formulas that encode
combinatorial problems or that come  from research in Proof Complexity
[3]_.

The  main  entry point  for  the  library is  the  ..py:cnfformula.CNF
object. A simple example its usage is the following

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
   c Generated with `cnfgen` (C) Massimo Lauria <lauria@kth.se>
   c https://github.com/MassimoLauria/cnfgen.git
   c
   p cnf 2 3
   1 -2 0
   -1 0
   2 0
   >>> print F.latex()
   % Generated with `cnfgen` (C) Massimo Lauria <lauria@kth.se>
   % https://github.com/MassimoLauria/cnfgen.git
   %
   \begin{align}
   &       \left(     {X} \lor \neg{Y} \right) \\
   & \land \left( \neg{X} \right) \\
   & \land \left(     {Y} \right)
   \end{align}

A very typical  formula studied in Proof Complexity  is the pigeonhole
principle formula,

   >>> from cnfformula.families import PigeonholePrinciple
   >>> F = PigeonholePrinciple(5,4)
   >>> print F.dimacs()
   c Pigeonhole principle formula for 5 pigeons and 4 holes
   c Generated with `cnfgen` (C) Massimo Lauria <lauria@kth.se>
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
   c Generated with `cnfgen` (C) Massimo Lauria <lauria@kth.se>
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

