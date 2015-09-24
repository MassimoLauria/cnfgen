   
How to build and use a CNF
==========================

The  basic   entry  point  of  the   :py:mod:`cnfformula`  library  is
:py:class:`cnfformula.CNF`,  which   is  the  representation   of  CNF
formulas. Any  string (or actually  any `hashable` object) is  a valid
name for  a variable, that can  be documented with an  additional (and
optional) description.

   >>> from cnfformula import CNF
   >>> F = CNF()
   >>> F.add_variable("X",'this variable is the cause')
   >>> F.add_variable("Y",'this variable is the effect')
   >>> F.add_variable("Z") # no variable description here

Clauses are  represented as lists  of literals, where each  literal is
either  positive  or  negative,  and  it  is  represented  as  ``(True
,<varname>)`` or ``((False,  <varname>))``, respectively. The addition
of variable and clauses can be interleaved.

   >>> F.add_clause([(False,"X"),(True,"Y")])
   >>> F.add_variable("W")
   >>> F.add_clause([(False,"Z")])

Now ``F`` encodes the formula 

.. math::

   ( \neg X \vee Y ) \wedge ( \neg Z)
   
over variables  :math:`X`, :math:`Y`,  :math:`Z` and :math:`W`.  It is
perfectly fine,  maybe wasteful though,  to add variables that  do not
occur in  any clause. Vice versa,  it is possible to  add clauses that
mention new  variables never  added before. In  that case  any unknown
variable  is silently  added  to the  formula  (obviously without  any
description).

   >>> G = CNF()
   >>> list(G.variables())
   []
   >>> G.add_clause([(False,"X"),(True,"Y")])
   >>> list(G.variables())
   ['X','Y']
   
.. note::

   By default the  :py:func:`cnfformula.CNF.add_clause` method forbids
   a  clauses to  contain  the  same literal  twice  and  to have  two
   opposite literlas (i.e.  a negative and a positive  literal one the
   same variable).  Furthermore, as mention  before, it allows  to add
   clauses with unknown variables.

   It is possible  to make the behavior either looser  or stricter, or
   anything in between.  For example it is possible  to allow opposite
   literals, but simultaneously forbid unknown variables.

   See the  documentation of  :py:func:`cnfformula.CNF.add_clause` for
   further details.

It is furthermore possible to  add clauses directly while constructing
the object.

   >>> H = CNF([ [(True,"x1"),(True,"x2"),(False,"x3"), [(False,"x2"),(True,"x4")] ])


Exporting formulas to DIMACS
----------------------------

One of the main use of ``CNFgen``  is to produce formulas to be fed to
SAT  solvers. These  solvers accept  the DIMACS  format for  CNF [1]_,
which can easily be obtained using :py:func:`cnfformula.CNF.dimacs`.

   >>> c=CNF([ [(True,"x1"),(True,"x2"),(False,"x3")], [(False,"x2"),(True,"x4")] ])
   >>> print( c.dimacs(export_header=False) )
   p cnf 4 2
   1 2 -3 0
   -2 4 0
   >>> c.add_clause( [(False,"x3"),(True,"x4"),(False,"x5")] )
   >>> print( c.dimacs(export_header=False))
   p cnf 5 3
   1 2 -3 0
   -2 4 0
   -3 4 -5 0

The variables in  the DIMACS representation are  numbered according to
the order of insertion. Adding  the variables explicitly before adding
the clauses ensures a specific order.

Exporting formulas to LaTeX
----------------------------

It is possible  to use :py:func:`cnfformula.CNF.latex` to  get a LaTeX
[2]_ encoding of  the CNF to include  in a document. In  that case the
variable names  are included literally,  therefore it is  advisable to
use variable names that would look good in Latex.

   >>> c=CNF([[(False,"x_1"),(True,"x_2"),(False,"x_3")],\
   ... [(False,"x_2"),(False,"x_4")], \
   ... [(True,"x_2"),(True,"x_3"),(False,"x_4")]])
   >>> print(c.latex(export_header=False))
   \begin{align}
   &       \left( {\overline{x}_1} \lor            {x_2} \lor {\overline{x}_3} \right) \\
   & \land \left( {\overline{x}_2} \lor {\overline{x}_4} \right) \\
   & \land \left( {x_2} \lor {x_3} \lor {\overline{x}_4} \right)
   \end{align}

which renders as

.. math::

   \begin{align}
   &       \left( {\overline{x}_1} \lor            {x_2} \lor {\overline{x}_3} \right) \\
   & \land \left( {\overline{x}_2} \lor {\overline{x}_4} \right) \\
   & \land \left( {x_2} \lor {x_3} \lor {\overline{x}_4} \right)
   \end{align}

Reference
---------
.. [1] http://www.satlib.org/Benchmarks/SAT/satformat.ps
.. [2] http://www.latex-project.org/ 
