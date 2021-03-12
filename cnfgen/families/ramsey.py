#!/usr/bin/env python
"""CNF Formulas for Ramsey-like statements
"""


from textwrap import dedent
from itertools import combinations
from math import sqrt

from cnfgen.formula.cnf import CNF
from cnfgen.localtypes import positive_int, positive_int_seq

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
    positive_int(N, 'N')

    description = "Pythagorean triples problem on 1...{}".format(N)
    F = CNF(description=description)

    if not isinstance(N, int):
        raise TypeError("argument N expected to be a non negative integer")
    if N < 0:
        raise ValueError("argument N expected to be a non negative integer")

    # Variables represent the coloring of the number
    v = F.new_block(N, label='v({})')

    for x, y in combinations(range(1, N + 1), 2):
        z = int(sqrt(x**2 + y**2))
        if z <= N and z**2 == x**2 + y**2:
            F.add_clause([+v(x), +v(y), +v(z)])
            F.add_clause([-v(x), -v(y), -v(z)])

    return F


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
    positive_int(N, 'N')
    positive_int(s, 's')
    positive_int(k, 'k')
    description = "{}-vertices graph free of {}-independent sets and {}-cliques".format(N, s, k)
    ram = CNF(description=description)

    # One variable per edge (indices are ordered)
    e = ram.new_combinations(N, 2, label='e_{{{}}}')

    # No independent set of size s
    for vertex_set in combinations(range(1, N + 1), s):
        clause = [e(u, v) for u, v in combinations(vertex_set, 2)]
        ram.add_clause(clause)

    # No clique of size k
    for vertex_set in combinations(range(1, N + 1), k):
        clause = [-e(u, v) for u, v in combinations(vertex_set, 2)]
        ram.add_clause(clause)

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
    positive_int(N,'N')
    positive_int(k1,'k1')
    positive_int(k2,'k2')
    positive_int_seq(ks, '*ks')

    K = [k1, k2] + list(ks)
    K_text = ", ".join(str(k) for k in K)
    description = "is van der Waerden number vdw({1}) > {0} ?".format(
        N, K_text)
    vdw = CNF(description=description)

    # Only one row of variable needed for 2 colors.
    if len(K) == 2:
        X = vdw.new_block(N, label='x_{{{}}}')

        for ap in _vdw_ap_generator(N, K[0]):
            vdw.add_clause([X(i) for i in ap])

        for ap in _vdw_ap_generator(N, K[1]):
            vdw.add_clause([-X(i) for i in ap])

    else:
        X = vdw.new_block(N, len(K), label='x_{{{0},{1}}}')
        for i in range(1, N + 1):
            vdw.add_linear(X(i, None), '==', 1)

        # Forbid arithmetic progressions
        for c in range(1,len(K)+1):
            for ap in _vdw_ap_generator(N, K[c - 1]):
                vdw.add_clause([-X(i, c) for i in ap])
    return vdw
