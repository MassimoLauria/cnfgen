Testing satisfiability
===========================

To   test  the   satisfiability  of   the  CNF   formula  encoded   in
a    :py:class:`cnfformula.CNF`    instance    we    can    use    the
:py:func:`cnfformula.CNF.is_satisfiable`                       method.
Testing satisfiability of a CNF is not at all considered to be an easy
task.  In  full   generality  the  problem  is   NP-hard  [1]_,  which
essentially means that there are no fast algorithm to solve it.

In practice  many formula  that come from  applications can  be solved
efficiently  (i.e.  it  is  possible  to  rapidly  find  a  satisfying
assignment). There is  a whole community of  clever software engineers
and computer scientists  that compete to write the  fastest solver for
CNF satisfiability (usually  called a SAT solver)  [2]_. `CNFgen` does
not  implement a  SAT  solver, but  uses behind  the  scenes the  ones
installed in  the running environment.  If the formula  is satisfiable
the value returned includes a satisfying assignment.

   >>> from cnfformula import CNF
   >>> F = CNF([ [(True,'X'),(False,'Y')], [(False,'X')] ])
   >>> F.is_satisfiable()
   (True, {'X': False, 'Y': False})
   >>> F.add_clause([(True,'Y')])
   >>> F.is_satisfiable()
   (False, None)

It is always possible to force ``CNFgen`` to use a specific solver or
a specific  command line invocation  using the ``cmd``  parameters for
:py:func:`cnfformula.CNF.is_satisfiable`.  ``CNFgen``   knows  how  to
interface with several  SAT solvers but when the  command line invokes
an  unknown solver  the  parameter ``sameas``  can  suggest the  right
interface to use.

   >>> F.is_satisfiable(cmd='minisat -no-pre')
   >>> F.is_satisfiable(cmd='glucose -pre')
   >>> F.is_satisfiable(cmd='lingeling --plain')
   >>> F.is_satisfiable(cmd='sat4j')
   >>> F.is_satisfiable(cmd='my-hacked-minisat -pre',sameas='minisat')
   >>> F.is_satisfiable(cmd='patched-lingeling',sameas='lingeling')


.. [1] NP-hardness is a fundamental  concept coming from computational
       complexity, which is  the mathematical study of how  hard is to
       perform certain computations.

       (https://en.wikipedia.org/wiki/NP-hardness)

.. [2] See http://www.satcompetition.org/ for SAT solver ranking.
