#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Implementation of Thapen's size-width tradeoff formula
"""

from itertools import product

from cnfgen.cnf import CNF


def CPLSFormula(a, b, c):
    """Thapen's size-width tradeoff formula

    The formula is a propositional version of the coloured polynomial
    local search principle (CPLS). A description can be found in [1]_.

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
    if a <= 0:
        raise ValueError("a must be positive.")
    if b <= 0 or b & (b - 1):
        raise ValueError("b must be a power of two.")
    if c <= 0 or c & (c - 1):
        raise ValueError("c must be a power of two.")

    log_b = 0
    while 2**log_b < b:
        log_b += 1
    log_c = 0
    while 2**log_c < c:
        log_c += 1

    description = "Thapen's CPLS formula with {} levels, {} nodes per level, {} colours".format(
        a, b, c)
    formula = CNF(description=description)

    # this allows notation G[i](x, y) and similar, which looks more like G_{i}(x, y) than G(i, x, y)
    class func_list(list):
        def __init__(self, f):
            self.f = f

        def __getitem__(self, key):
            return self.f(key)

    # TODO: Is "log a" a typo in "3." of the variables definition? I assume it's "log c".

    # G_i(x, y) -> G[i](x, y)
    G = func_list(lambda i: lambda x, y: 'G_{{{0}}}({1},{2})'.format(i, x, y))
    # (f_i(x))_j -> f[i](x)[j]
    f = func_list(lambda i: lambda x: func_list(
        lambda j: '(f_{{{0}}}({1}))_{{{2}}}'.format(i, x, j)))
    # (u(x))_j -> u(x)[j]
    u = lambda x: func_list(lambda j: '(u({0}))_{{{1}}}'.format(x, j))

    # 1. For each i < a, x < b and y < c, there is a variable G_i(x,y).
    for i, x, y in product(range(a), range(b), range(c)):
        formula.add_variable(G[i](x, y))
    # 2. For each i < a, x < b and j < log b, there is a variable (f_i(x))_j,
    #    standing for the j'th bit of the value of f_i(x).
    for i, x, j in product(range(a), range(b), range(log_b)):
        formula.add_variable(f[i](x)[j])
    # 3. For each x < b and j < log a, there is a variable (u(x))_j,
    #    standing for the j'th bit of the value of u(x).
    for x, j in product(range(b), range(log_c)):
        formula.add_variable(u(x)[j])

    # x_{bits-1}..x_0 != binary(x'), encoded as the disjunction of l_j for all j,
    # where l_j = ~x_j if the j'th bit of x' is 1, and l_j = x_j otherwise.
    def bin_ineq(f_i_x, x_prime, bits):
        return [(not bool(x_prime & (1 << j)), f_i_x[j]) for j in range(bits)]

    # 1. For each y < c, the clause ~G_0(0, y)
    for y in range(c):
        formula.add_clause([(False, G[0](0, y))], strict=True)
    # 2. For each i < a-1, each pair x,x' < b and each y < c,
    #    the clause f_i(x) = x' ^ G_{i+1}(x', y) -> G_i(x, y)
    for i, x, x_, y in product(range(a - 1), range(b), range(b), range(c)):
        formula.add_clause(bin_ineq(f[i](x), x_, log_b) +
                           [(False, G[i + 1](x_, y)), (True, G[i](x, y))],
                           strict=True)
    # 3. For each x < b and each y < c, the clause u(x) = y -> G_{a-1}(x, y)
    for x, y in product(range(b), range(c)):
        formula.add_clause(bin_ineq(u(x), y, log_c) + [(True, G[a - 1](x, y))],
                           strict=True)

    return formula
