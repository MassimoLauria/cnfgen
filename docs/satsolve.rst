Testing satisfiability
===========================

It is possible to test the  satisfiability of a CNF formula. We stress
that testing satisfiability of a CNF is not at all considered to be an
easy  task. In  full generality  the  problem is  NP-hard [1]_,  which
essentially means that there are no fast algorithm to solve it.

In practice many formula that come from industrial applications can be
solved efficiently (i.e.  it is possible to rapidly  find a satisfying
assignment). There  is a whole  pack of clever software  engineers and
computer scientists that  compete to write the fastest  solver for CNF
satisfiability (usually called a SAT solver). [2]_

`CNFgen`  does not  implement  a SAT  solver, but  will  use the  ones
installed in the  running environment. If any of  the supported solver
is  found in  the  system  `CNFgen` will  use  it  behind the  scenes.
Nevertheless it is always possible to force `CNFgen` a specific solver
and a  specific command line  invocation. It  is also possible  to use
a non supported  solver, as long as its interface  is identical to the
interface of a supported one.


.. [1] NP-hardness is a fundamental  concept coming from computational
       complexity, which is  the mathematical study of how  hard is to
       perform                  certain                  computations.
       (https://en.wikipedia.org/wiki/NP-hardness)
       
.. [2] http://www.satcompetition.org/
