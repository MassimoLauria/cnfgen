The command line utility
========================

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
