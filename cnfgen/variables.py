#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Keep tracks of the variable of a formula.

The module defines a variable manager, that formulas could either use
of specialize. It allows to generates
- single variables
- variables for some tuples of indices
- variables for the edges of a graph
- variables for vertices of a graph

The module implements the :py:class:`VariablesManager` object, which
is supposed to be inherited from the :py:class:`CNF` object.

Copyright (C) 2019-2021  Massimo Lauria <lauria.massimo@gmail.com>
https://github.com/MassimoLauria/cnfgen.git

"""
from functools import reduce
from operator import mul
from itertools import product
from bisect import bisect_right


class BlockOfVariables():
    """Represents a group of variables indexed by a cartesian product
of ranges.

    This objects represents groups of variables that are indexed by
    some tuples of integers. For example we can have variables
    :math:`p_{i,j}` for :math:`i in [10]` and :math:`j in [7]`.

    A group can have an arbitrary number of indices, each ranging
    independently between :math:`1` and some arbitrary integer.

    This object is meant to be used internally by
    :py:class:`VariablesManager`.

    Examples
    --------
    >>> G = BlockOfVariables(21,[2,3],'G[{},{}]')
    >>> print(*G.label())
    G[1,1] G[1,2] G[1,3] G[2,1] G[2,2] G[2,3]
    >>> print(*G.indices())
    (1, 1) (1, 2) (1, 3) (2, 1) (2, 2) (2, 3)
    >>> G(2,1)
    24
    >>> V = VariablesManager()
    >>> p = V.new_block(10,5,label='p({},{})')
    >>> q = V.new_block(3,3,label='q({},{})')
    >>> isinstance(p,BlockOfVariables)
    True
    >>> print(len(p))
    50
    >>> print(len(q))
    9
    >>> print(p.to_index(23))
    [5, 3]
    >>> print(q.to_index(54))
    [2, 1]
    >>> print(list(q.indices()))
    [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (3, 3)]
    >>> print(p(2,3))
    8
    >>> print(list( p(None,3) ))
    [3, 8, 13, 18, 23, 28, 33, 38, 43, 48]
    >>> print(q(1,1))
    51
    >>> 52 in q
    True
    >>> 12 in q
    False
    >>> print(q.label(1,1))
    q(1,1)
    >>> print(*q.label(2,None))
    q(2,1) q(2,2) q(2,3)
    >>> print(p.label(4,2))
    p(4,2)
    >>> print(list(p.indices(3,None)))
    [(3, 1), (3, 2), (3, 3), (3, 4), (3, 5)]
    >>> print(p.to_index(p(4,3)))
    [4, 3]

    """
    def __init__(self, startID, ranges, labelfmt=None):
        """Creates a variables group object

        Parameters
        ----------
        startID: integer
            start variables IDs from this number
        ranges: list(integer)
            ranges of the indices
        labelfmt: str
            format string for the variable labels
        """
        if startID < 1:
            raise ValueError('Variables group must start at index >=1')
        if len([x for x in ranges if x < 1]):
            raise ValueError('Indices range must be all positive')

        self.ranges = ranges
        weights = [1]  # cumulative products
        for r in ranges[::-1]:
            weights.append(weights[-1] * r)

        if labelfmt is None:
            labelfmt = 'X(' + ','.join(['{}'] * len(ranges)) + ')'
        # Check if the format strings can get all parameters
        try:
            labelfmt.format(*ranges)
        except IndexError:
            raise ValueError(
                'label must be a valid format string for all indices')

        self.ranges = ranges
        self.N = weights.pop()  # number of variables
        self.weights = weights[::-1]
        self.labelfmt = labelfmt
        self.startID = startID

    def __call__(self, *index):
        """Convert the index of a variable into its ID.

        A variable is identified by an integer ID, but if it is one of
        the variables of a group, it has an associate tuple as index.
        This function convert the indices into the corresponding ID.

        Parameters
        ----------
        index : sequences(positive integers)
            the index of the variable
       
        Returns
        -------
            int

        Raises
        ------
        ValueError
            when the indices are not within the ranges
        """
        if len(index) != len(self.ranges):
            raise ValueError("Index arity do not match the ranges {}".format(
                self.ranges))

        try:
            offset = sum((i - 1) * w for i, w in zip(index, self.weights))
            assert 0 <= offset < self.N
            return offset + self.startID
        except TypeError:
            pass

        def _gen():
            for idxs in self.indices(*index):
                offset = sum((i - 1) * w for i, w in zip(idxs, self.weights))
                yield offset + self.startID

        return _gen()

    def __len__(self):
        return self.N

    def __contains__(self, ID):
        return 0 <= (ID - self.startID) < self.N

    def label(self, *pattern):
        if len(pattern) > 0 and len(pattern) != len(self.ranges):
            raise ValueError("Wrong number of indices in the pattern")

        if len(pattern) == 0:
            pattern = [None] * len(self.ranges)

        if None not in pattern:
            return self.labelfmt.format(*pattern)

        def _gen():
            for idxs in self.indices(*pattern):
                yield self.labelfmt.format(*idxs)

        return _gen()

    def indices(self, *pattern):
        if len(pattern) > 0 and len(pattern) != len(self.ranges):
            raise ValueError("Wrong number of indices in the pattern")

        if len(pattern) == 0:
            pattern = [None] * len(self.ranges)

        # non trivial patterns
        x = []
        for i, R in zip(pattern, self.ranges):
            if i is None:
                x.append(range(1, R + 1))
            elif 1 <= i <= R:
                x.append((i, ))
            else:
                raise ValueError("Invalid index in the pattern")

        return product(*x)

    def to_index(self, lit):
        """Convert a literal of the index sequence corresponding to the variable

        A variable is identified by an integer id, but an associate
        index in the variable group. This function convert the
        variable id into such index. If a negative literal is given,
        the function returns the index of the corresponding variable.

        Parameters
        ----------
        var : positive integer
            the ID of the variable

        Returns
        -------
            sequence(positive integers)

        Raises
        ------
        ValueError
            when `var` is not within the appropriate interval

        Examples
        --------
        >>> VG = BlockOfVariables(1,[3,5,4,3])
        >>> VG.to_index(1)
        [1, 1, 1, 1]
        >>> VG.to_index(5)
        [1, 1, 2, 2]
        >>> VG.to_index(179)
        [3, 5, 4, 2]
        >>> VG.to_index(180)
        [3, 5, 4, 3]

        """
        var = abs(lit)
        if var not in self:
            raise ValueError('Index out of range')

        index = []
        residue = var - self.startID
        for w in self.weights:
            index.append(residue // w + 1)
            residue = residue % w
        return index


class VariablesManager():
    """Manager for some formula variables.

    A CNF formula needs to keep track on variables.
    A :py:class:`VariableManager` object allows to do that, while
    providing a nice interface that allows to focus on variable meaning.

    Internally a variable is represented as an integer, as in DIMACS,
    and all variables are indexed from 1 to :math:`N` which would be
    the number of variables (i.e. no gaps). Literals will be
    represented with the same number, multiplied by 1 and -1,
    respectively, to indicate the positive and negative versions.

    Implementation: instead of having info for each variables, we use
    a sparse representation. Each list with info is essentially a list
    containing the larger index of each group, searchable with
    :py:func:`bisect_right` and moving one step left.

    Attributes
    ----------
    name : dict
        associate a variable / literal to its label

    Methods
    -------
    new_variable(label=''):
        add a new variable

    new_block(*ranges,label=''):
        add variables with one or more indices

    vars():
        enumerates all variables

    varnames():
        enumerate the names of all variables

    Examples
    --------
    >>> V=VariablesManager()
    >>> X = V.new_variable(label="X")
    >>> Y = V.new_variable(label="Y")
    >>> Zs = V.new_block(2,3,label='z_{{{},{}}}')
    >>> len(V)
    8
    >>> len(Zs)
    6
    >>> print(*V.varnames())
    X Y z_{1,1} z_{1,2} z_{1,3} z_{2,1} z_{2,2} z_{2,3}
    """
    def __init__(self):
        """Construct a variable manager object
        """

        self.groups = []
        self.info = {}

    def new_variable(self, label=None):
        """
        Create a new variable

        Parameters
        ----------
        label : str, optional
            string representation of the variables

        Returns
        -------
        int, the new variable

        Examples
        --------
        >>> V=VariablesManager()
        >>> V.new_variable(label='X')
        1
        >>> len(V)
        1
        >>> V.new_variable(label='Y')
        2
        >>> V.new_variable(label='Z')
        3
        >>> len(V)
        3
        """
        newvar = len(self) + 1
        self.groups.append(newvar)
        if label is None:
            label = 'x{}'.format(newvar)
        self.info[newvar] = label
        return newvar

    def new_block(self, *ranges, label=None):
        """
        Create a new group of indexed variables

        Parameters
        ----------
        ranges : iterable(positive integer)
            the range of the variable indices

        label : str, optional
            string representation of the variables

        Returns
        -------
        BlockOfVariables, the new variable group

        Examples
        --------
        >>> V=VariablesManager()
        >>> V.new_variable(label='X')
        1
        >>> len(V)
        1
        >>> V.new_variable(label='Y')
        2
        >>> V.new_variable(label='Z')
        3
        >>> len(V)
        3
        >>> v = V.new_block(3,5,4,3,label='v({},{},{},{})')
        >>> v.to_index(4)
        [1, 1, 1, 1]
        >>> v(1,1,1,1)
        4
        >>> v.to_index(8)
        [1, 1, 2, 2]
        >>> v(1,1,2,2)
        8
        >>> v.to_index(182)
        [3, 5, 4, 2]
        >>> v(3,5,4,2)
        182
        >>> v.to_index(183)
        [3, 5, 4, 3]
        >>> v(3,5,4,3)
        183
        """
        newgroup = BlockOfVariables(len(self) + 1, ranges, label)
        self.groups.append(len(self) + len(newgroup))
        self.info[self.groups[-1]] = newgroup

        return newgroup

    def __len__(self):
        if len(self.groups) == 0:  # no variables
            return 0
        else:
            return self.groups[-1]  # last set of variables

    def varnames(self):
        """Enumerate variable names

        Generator enumerates all variables by name.
        """
        for x in self.groups:
            varinfo = self.info[x]
            if isinstance(varinfo, str):
                yield varinfo
            else:
                yield from varinfo.label()
