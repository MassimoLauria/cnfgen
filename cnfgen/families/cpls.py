#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of Thapen's size-width tradeoff formula
"""

from itertools import product

from cnfgen.formula.cnf import CNF
from cnfgen.localtypes import positive_int


def intlog2(x):
    """Compute the ceiling of the log2(x)"""
    ilog = 0
    while 2**ilog < x:
        ilog += 1
    return ilog


def CPLSFormula(a, b, c, formula_class=CNF):
    """Thapen's size-width tradeoff formula

    The formula is a propositional version of the coloured polynomial
    local search principle (CPLS). A description can be found in [1]_.
    The difference with the formula in the paper is that here unary
    indices start from 1 instead of 0. Binary strings stil counts from
    0, therefore the mappings :math:`f[i](x)=x'` is actually
    represented in binary with the binary representation
    of :math:`x'-1`.

    Parameters
    ----------
    a: integer
       number of levels
    b: integer
       nodes per level (must be a power of 2)
    c: integer
       number of colours (must be a power of 2)

    References
    ----------
    .. [1] N. Thapen (2016)
           Trade-offs between length and width in resolution.
           Theory of Computing, 12(1), 1–14.

    """
    positive_int(a, 'a')
    positive_int(b, 'b')
    positive_int(c, 'c')
    if b & (b - 1):
        raise ValueError("b must be a power of two.")
    if c & (c - 1):
        raise ValueError("c must be a power of two.")

    description = "Thapen's CPLS formula with {} levels, {} nodes per level, {} colours".format(a, b, c)
    F = formula_class(description=description)

    # 1. For each 1 <= i <= a, 1 <= x <= b and 1 <= y <= c
    # G_i(x, y)
    G = F.new_block(a, b, c, label='G_{}({},{})')

    # 2. For each 1 <= i <= a, 1 <= x <= b and j < log b
    # (f_i(x))_j
    f = [None]
    for i in range(1,a+1):
        ilabel = '(f_{{'+str(i)+'}}'+'({}))_{{{}}}'
        f.append(F.new_binary_mapping(b, b, label=ilabel))

    # 3. For each 1 <= x <= b and j < log c, there is a variable (u(x))_j,
    # (u(x))_j
    u = F.new_binary_mapping(b, c, label='(u({0}))_{{{1}}}')

    # Axiom 1. For each 1 <= y <= c, the clause ~G_1(1, y)
    for var in G(1, 1, None):
        F.add_clause([-var])

    # Axiom 2. For each 1 <= i < a, each pair x,x' in [b] and each [c],
    #    the clause f_i(x) = x' ^ G_{i+1}(x', y) -> G_i(x, y)
    domains = product(range(1, a),
                      range(1, b+1),
                      range(1, b+1),
                      range(1, c+1))
    for i, x, xx, y in domains:
        first = f[i].forbid(x, xx - 1)
        F.add_clause(first + [-G(i+1, xx, y), G(i, x, y)])

    # Axiom 3. For each 1 <= x <= b and each 1 <= y <= c,
    #     the clause u(x) = y-1 -> G_{a}(x, y)
    for x, y in product(range(1, b+1), range(1, c+1)):
        F.add_clause(u.forbid(x, y - 1) + [G(a, x, y)])

    nvars = a*b*c + a*b*intlog2(b) + b*intlog2(c)
    ncls = c + (a-1)*b*b*c + b*c
    assert F.number_of_variables() == nvars
    assert len(F) == ncls
    return F
