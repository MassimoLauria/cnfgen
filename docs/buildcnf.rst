How to build a CNF
==================

The entry point to :py:mod:`cnfgen` library is :py:class:`cnfgen.CNF`,
which is the  data structure representing CNF  formulas. Variables can
have text names but  in general each variable is an  integer from 1 to
:math:`n`, where  :math:`n` is  the number of  variables.

   >>> from cnfgen import CNF
   >>> F = CNF()
   >>> x = F.new_variable("X")
   >>> y = F.new_variable("Y")
   >>> z = F.new_variable("Z")
   >>> print(x,y,z)
   1 2 3

A clause is a  list of literals, and each literal  is ``+v`` or ``-v``
where ``v``  is the number corresponding  to a variable. The  user can
interleave  the addition  of variables  and clauses.  Notice that  the
method :py:method:`new_variable`  return the  numeric id of  the newly
added variable, which can be optionally used to build clauses.

   >>> F.add_clause([-x, y])
   >>> w = F.new_variable("W")
   >>> w == 4
   True
   >>> F.add_clause([-z, 4])
   >>> F.number_of_variables()
   4
   >>> F.number_of_clauses()
   2
   
The CNF object ``F`` in the example now encodes the formula 

.. math::

   ( \neg X \vee Y ) \wedge ( \neg Z \vee W)
   
over variables  :math:`X`, :math:`Y`,  :math:`Z` and :math:`W`.  It is
perfectly  fine to  add variables  that do  not occur  in any  clause.
Vice versa, it is possible to add clauses that mention variables never
seen before.  In that case any  unknown variable is silently  added to
the formula.

   >>> G = CNF()
   >>> G.number_of_variables()
   0
   >>> G.add_clause([-1, 2])
   >>> G.number_of_variables()
   2
   >>> list(G.variables())
   [1, 2]
   
.. note::

   By default  the :py:method:`cnfgen.CNF.add_clause` checks  that all
   literals in the clauses are non-zero integers. Furthermore if there
   are new variables mentioned in  the clause, the number of variables
   of the formula  is automatically updated. This  checks makes adding
   clauses  a  bit expensive,  and  that's  an  issue for  very  large
   formulas where  millions of  clauses are added.  It is  possible to
   avoid such checks but then it  is resposibility of the user to keep
   things consistent.

   See also  :py:method:`cnfgen.CNF.debug`, which in turn  can be also
   used   to   check  the   presence   of   literal  repetitions   and
   opposite literals.
 
It is possible to add clauses directly at the CNF construction. The code

   >>> H = CNF([ [1,2,-3], [-2,4] ])

is essentially equivalent to

   >>> H = CNF()
   >>> H.add_clauses_from([ [1,2,-3], [-2,4] ])

or
   
   >>> H = CNF()
   >>> H.add_clause([1,2,-3])
   >>> H.add_clause([-2,4])


Exporting formulas to DIMACS
----------------------------

One of the main use of ``CNFgen``  is to produce formulas to be fed to
SAT solvers. These solvers accept CNf formulas in DIMACS format [1]_,
which can easily be obtained using :py:func:`cnfgen.CNF.to_dimacs`.

   >>> c=CNF([ [1,2,-3], [-2,4] ])
   >>> print( c.to_dimacs() )
   p cnf 4 2
   1 2 -3 0
   -2 4 0
   <BLANKLINE>
   >>> c.add_clause( [-3,4,-5] )
   >>> print( c.to_dimacs() )
   p cnf 5 3
   1 2 -3 0
   -2 4 0
   -3 4 -5 0
   <BLANKLINE>

The variables in  the DIMACS representation are  numbered according to
the order of  insertion. ``CNFgen`` does not  guarantee anything about
this order, unless variables are added explicitly.

Exporting formulas to LaTeX
----------------------------

It is possible  to use :py:func:`cnfgen.CNF.to_latex` to  get a LaTeX
[2]_ encoding of  the CNF to include  in a document. In  that case the
variable names  are included literally,  therefore it is  advisable to
use variable names that would look good in Latex. By default variables
``i`` has the assigned name ``x_{i}``.

   >>> c=CNF([[-1, 2, -3], [-2,-4], [2,3,-4]])
   >>> print(c.to_latex())
   \begin{align}
   &       \left( {\overline{x}_1} \lor            {x_2} \lor {\overline{x}_3} \right) \\
   & \land \left( {\overline{x}_2} \lor {\overline{x}_4} \right) \\
   & \land \left(            {x_2} \lor            {x_3} \lor {\overline{x}_4} \right)
   \end{align}

which renders as

.. math::

   \begin{align}
   &       \left( {\overline{x}_1} \lor            {x_2} \lor {\overline{x}_3} \right) \\
   & \land \left( {\overline{x}_2} \lor {\overline{x}_4} \right) \\
   & \land \left( {x_2} \lor {x_3} \lor {\overline{x}_4} \right)
   \end{align}

Instead of  outputting just the LaTeX  rendering of the formula  it is
possible to produce a full LaTeX document by using 
:py:func:`cnfgen.CNF.to_latex_document`. The document is ready to be compiled.

   
Reference
---------
.. [1] http://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/satformat.ps
.. [2] http://www.latex-project.org/ 
