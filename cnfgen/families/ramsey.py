#!/usr/bin/env python
"""CNF Formulas for Ramsey-like statements
"""

from cnfgen.formula.cnf import CNF

from textwrap import dedent
from itertools import combinations
from math import sqrt


def PythagoreanTriples(N):
    """There is a Pythagorean triples free coloring on N

    The formula claims that it is possible to bicolor the numbers from
    1 to :math:`N` so that there  is no monochromatic triplet
    :math:`(x,y,z)` so that :math:`x^2+y^2=z^2`.

    Parameters
    ----------
    N  : int
         size of the interval

    Return
    ------
    A CNF object

    Raises
    ------
    ValueError
       Parameters are not positive
    TypeError
       Parameters are not integers

    References
    ----------
    .. [1] M. J. Heule, O. Kullmann, and V. W. Marek.
           Solving and verifying the boolean pythagorean triples problem via cube-and-conquer.
           arXiv preprint arXiv:1605.00723, 2016.
    """

    description = "Pythagorean triples problem on 1...{}".format(N)
    ptn = CNF(description=description)

    if not isinstance(N, int):
        raise TypeError("argument N expected to be a non negative integer")
    if N < 0:
        raise ValueError("argument N expected to be a non negative integer")

    def V(i):
        return "x_{{{}}}".format(i)

    # Variables represent the coloring of the number
    for i in range(1, N + 1):
        ptn.add_variable(V(i))

    for x, y in combinations(range(1, N + 1), 2):
        z = int(sqrt(x**2 + y**2))
        if z <= N and z**2 == x**2 + y**2:
            ptn.add_clause([(True, V(x)), (True, V(y)), (True, V(z))],
                           strict=True)
            ptn.add_clause([(False, V(x)), (False, V(y)), (False, V(z))],
                           strict=True)

    return ptn


def RamseyNumber(s, k, N):
    """Ramsey number r(s,k) > N

    This formula, given :math:`s`, :math:`k`, and :math:`N`, claims
    that there is some graph with :math:`N` vertices which has neither
    independent sets of size :math:`s` nor cliques of size :math:`k`.

    It turns out that there is a number :math:`r(s,k)` so that every
    graph with at least :math:`r(s,k)` vertices must contain either
    one or the other. Hence the generated formula is satisfiable if
    and only if

    .. math::

         r(s,k) > N

    Parameters
    ----------
    s  : int
         independent set size
    k  : int
         clique size
    N  : int
         number of vertices

    Returns
    -------
    A CNF object

    Raises
    ------
    ValueError
       Parameters are not positive
    TypeError
       Parameters are not integers

    """

    description = "{}-vertices graph free of {}-independent sets and {}-cliques".format(
        N, s, k)
    ram = CNF(description=description)

    if not isinstance(N, int):
        raise TypeError("argument N expected to be a positive integer")
    if N < 1:
        raise ValueError("argument N expected to be a positive integer")

    if not (isinstance(s, int) and isinstance(k, int)):
        raise TypeError("arguments s,k expected to be positive integers")
    if s < 1 or k < 1:
        raise ValueError("arguments s,k expected to be positive integers")

    def V(i):
        return "x_{{{}}}".format(i)

    #
    # One variable per edge (indices are ordered)
    #
    for edge in combinations(range(1, N + 1), 2):
        ram.add_variable('e_{{{0},{1}}}'.format(*edge))

    #
    # No independent set of size s
    #
    for vertex_set in combinations(range(1, N + 1), s):
        clause = []
        for edge in combinations(vertex_set, 2):
            clause += [(True, 'e_{{{0},{1}}}'.format(*edge))]
        ram.add_clause(clause, strict=True)

    #
    # No clique of size k
    #
    for vertex_set in combinations(range(1, N + 1), k):
        clause = []
        for edge in combinations(vertex_set, 2):
            clause += [(False, 'e_{{{0},{1}}}'.format(*edge))]
        ram.add_clause(clause, strict=True)

    return ram


def _vdw_ap_generator(N, k):
    '''Generates arithmetic progressions of length k in 1...N'''

    # the largest gap d must be such that
    # 1+ d*(k-1) <= N
    # so d <= (N-1)/(k-1)
    max_d = (N - 1) // (k - 1)
    for d in range(1, max_d + 1):
        max_i = N - d * k + d
        for i in range(1, max_i + 1):
            yield [i + d * t for t in range(k)]


def VanDerWaerden(N, k1, k2, *ks):
    """Formula claims that van der Waerden number vdw(k1,k2,k3,k4,...) > N

    Consider a coloring the of integers from 1 to :math:`N`, with
    :math:`d` colors. The coloring has an arithmetic progression of
    color :math:`c` of length :math:`k` if there are :math:`i` and
    :math:`d` so that all numbers

    .. math::

         i, i+d, i+2d, \ldots, i +(k-1)d

    have color :math:`c`. In fact, given any number of lengths
    :math:`k_1`, :math:`k_2`,..., :math:`k_C`, there is some value of
    :math:`N` large enough so that no matter how the integers
    :math:`1, \ldots, N` are colored with :math:`C` colors, such
    coloring must have one arithmetic progression of color
    :math:`c` and length :math:`k_c`.

    The smallest :math:`N` such that it is impossible to avoid the
    arithmetic progression regardless of the coloring is called van
    der Waerden number and is denotes as

    .. math::

         VDW(k_1, k_2 , \ldots, k_C)

    The formula, given :math:`N` and :math`k_1`, :math`k_2` , \ldots,
    :math`k_C`, is the CNF encoding of the claim

    .. math::

         VDW(k_1, k_2 , \ldots, k_C) > N

    which is expressed, more concretely, as a CNF which forbids, for
    each color :math:`c` between 1 and :math:`C`, all arithmetic
    progressions of length :math:`k_C`

    Parameters
    ----------
    N : int
        size of the interval
    k1: int
        length of the arithmetic progressions of color 1
    k2: int
        length of the arithmetic progressions of color 2
    *ks : optional
        lengths of the arithmetic progressions of color >2

    Returns
    -------
    A CNF object

    Raises
    ------
    ValueError
       Parameters are not positive
    TypeError
       Parameters are not integers
    """

    for v in [N, k1, k2] + list(ks):
        if not isinstance(v, int):
            raise TypeError("all parameters expected to be positive integers")
        if v < 1:
            raise ValueError("all parameters expected to be positive integers")

    K = [k1, k2] + list(ks)
    K_text = ", ".join(str(k) for k in K)
    description = "is van der Waerden number vdw({1}) > {0} ?".format(
        N, K_text)
    vdw = CNF(description=description)

    colors = range(1, len(K) + 1)

    # Use unary functional mapping for >2 colorings
    if len(colors) > 2:
        # Use unary functional mapping for >2 colorings
        def Var(i, c):
            return "x_{{{},{}}}".format(i, c)

        def Not(i, c):
            return (False, Var(i, c))
    else:
        # Use a single binary variable for 2-colorings
        def Var(i, c):
            return "x_{{{}}}".format(i)

        def Not(i, c):
            if c == 1:
                return (True, Var(i, c))
            else:
                return (False, Var(i, c))

    # Only one row of variable needed for 2 colors.
    if len(colors) == 2:
        for i in range(1, N + 1):
            vdw.add_variable(Var(i, 1))
    else:
        # For more than two color we need all variables
        for c in colors:
            for i in range(1, N + 1):
                vdw.add_variable(Var(i, c))
        # I need to pick exactly one color index
        for i in range(1, N + 1):
            for cls in CNF.equal_to_constraint([Var(i, c) for c in colors], 1):
                vdw.add_clause(cls)

    # Forbid arithmetic progressions
    for c in colors:
        for ap in _vdw_ap_generator(N, K[c - 1]):
            vdw.add_clause([Not(i, c) for i in ap], strict=True)
    return vdw
