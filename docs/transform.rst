Post-process a CNF formula
==========================

After you produce a :py:class:`cnfformula.CNF`, maybe using one of the 
`generators  included  <families.html>`_,  it  is  still  possible  to
modify it. One simple  ways is to add new clauses  but there are ways
to  make  the formula  harder  with  some structured  transformations.
Usually this technique is employed to produce interesting formulas for
proof complexity applications or to benchmark SAT solvers.

Example: ``OR`` substitution
----------------------------

As an  example of formula  post-processing, we transform a  formula by
substituting every variable  with the logical disjunction  of, says, 3
fresh variables. Consider the following CNF as starting point.

.. math::

   ( \neg X \vee Y ) \wedge ( \neg Z)

After the substitution the new formula is still expressed as a CNF and
it is

.. math::

   ( \neg X_1 \vee Y_1 \vee Y_2 \vee Y_3) \wedge
   
   ( \neg X_2 \vee Y_1 \vee Y_2 \vee Y_3) \wedge

   ( \neg X_3 \vee Y_1 \vee Y_2 \vee Y_3) \wedge

   ( \neg Z_1)
   \wedge ( \neg Z_2)
   \wedge ( \neg Z_3)

There are many other  transformation methods than ``OR`` substitution.
Each method  comes with a  `rank` parameter that controls  the hardness
after the substitution. In the previous example the parameter would be
the  number of  variables used  in the  disjunction to  substitute the
original variables.

Using CNF transformations
-------------------------

We implement the following transformation methods. The ``none`` method
just leaves  the formula  alone. It  is a  null transformation  in the
sense that,  contrary to the  other methods, this one  returns exactly
the  same :py:class:`cnfformula.CNF`  object  that it  gets in  input.
All the  other methods  would produce  a new CNF  object with  the new
formula. The old one is left untouched.

*Some method implemented as still missing from the list*


+----------+----------------------------+--------------+----------------------------------------------------+
| *Name*   | Description                | Default rank | See documentation                                  | 
+----------+----------------------------+--------------+----------------------------------------------------+
| ``none`` | leaves the formula alone   |      ignored |                                                    |
+----------+----------------------------+--------------+----------------------------------------------------+
| ``eq``   | all variables equal        |            3 | :py:class:`cnfformula.AllEqualSubstitution`        |
+----------+----------------------------+--------------+----------------------------------------------------+
| ``ite``  | if x then y else z         |      ignored | :py:class:`cnfformula.IfThenElseSubstitution`      |
+----------+----------------------------+--------------+----------------------------------------------------+
| ``lift`` | lifting                    |            3 | :py:class:`cnfformula.FormulaLifting`              |
+----------+----------------------------+--------------+----------------------------------------------------+
| ``maj``  | Loose majority             |            3 | :py:class:`cnfformula.MajoritySubstitution`        |
+----------+----------------------------+--------------+----------------------------------------------------+
| ``neq``  | not all vars  equal        |            3 | :py:class:`cnfformula.NotAllEqualSubstitution`     |
+----------+----------------------------+--------------+----------------------------------------------------+
| ``one``  | Exactly one                |            3 | :py:class:`cnfformula.ExactlyOneSubstitution`      |
+----------+----------------------------+--------------+----------------------------------------------------+
| ``or``   | OR substitution            |            2 | :py:class:`cnfformula.OrSubstitution`              |
+----------+----------------------------+--------------+----------------------------------------------------+
| ``xor``  | XOR substitution           |            2 | :py:class:`cnfformula.XorSubstitution`             |
+----------+----------------------------+--------------+----------------------------------------------------+
                                                                                                            

Any  :py:class:`cnfformula.CNF`   can  be  post-processed   using  the
function   :py:func:`cnfformula.TransformFormula`.   For  example   to
substitute each variable with a 2-XOR we can do

   >>> from cnfformula import CNF, XorSubstitution
   >>> F = CNF([ [(True,"x1"),(True,"x2"),(False,"x3")], [(False,"x2"),(True,"x4")] ])
   >>> G = XorSubstitution(F,2)

Here is the original formula.

   >>> print( F.dimacs(export_header=False) )
   p cnf 4 2
   1 2 -3 0
   -2 4 0

Here it is after the transformation.
   
   >>> print( G.dimacs(export_header=False) )
   p cnf 8 12
   1 2 3 4 5 -6 0
   1 2 3 4 -5 6 0
   1 2 -3 -4 5 -6 0
   1 2 -3 -4 -5 6 0
   -1 -2 3 4 5 -6 0
   -1 -2 3 4 -5 6 0
   -1 -2 -3 -4 5 -6 0
   -1 -2 -3 -4 -5 6 0
   3 -4 7 8 0
   3 -4 -7 -8 0
   -3 4 7 8 0
   -3 4 -7 -8 0

It is possible  to omit the rank parameter. In  such case the default
value is used.
