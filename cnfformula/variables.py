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

Copyright (C) 2012-2020  Massimo Lauria <lauria.massimo@gmail.com>
https://github.com/MassimoLauria/cnfgen.git

"""
from functools import reduce
from operator import mul
from itertools import product


class VariablesGroup():
    """Represents a group of variables

    This objects represents groups of variables that are indexed by
    some tuples of integers. For example we can have variables
    :math:`p_{i,j}` for :math:`i in [10]` and :math:`j in [7]`.

    A group can have an arbitrary number of indices, each ranging
    independently between :math:`1` and some arbitrary integer.

    This object is meant to be used internally by
    :py:class:`VariablesManager`.

    Examples
    --------
    >>> G = VariablesGroup(21,[2,3],'G[{},{}]')
    >>> print(*G.label())
    G[1,1] G[1,2] G[1,3] G[2,1] G[2,2] G[2,3]
    >>> print(*G.indices())
    (1, 1) (1, 2) (1, 3) (2, 1) (2, 2) (2, 3)
    >>> G(2,1)
    24
    >>> V = VariablesManager()
    >>> p = V.new_variables(10,5,label='p({},{})')
    >>> q = V.new_variables(3,3,label='q({},{})')
    >>> isinstance(p,VariablesGroup)
    True
    >>> print(len(p))
    50
    >>> print(len(q))
    9
    >>> print(p.to_indices(23))
    [5, 3]
    >>> print(q.to_indices(54))
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
    >>> print(p.to_indices(p(4,3)))
    [4, 3]
    """
    def __init__(self, startID, ranges, labelfmt):
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
        self.ranges = ranges
        self.N = reduce(mul, self.ranges)
        self.labelfmt = labelfmt
        self.ID_offset = startID - 1

    def __call__(self, *indices):
        if len(indices) != len(self.ranges):
            raise ValueError("Indices do not match the ranges {}".format(
                self.ranges))

        if None not in indices:
            return self.indices_to_varoffset(indices,
                                             self.ranges) + self.ID_offset

        def _gen():
            for idxs in self.indices(*indices):
                yield self.indices_to_varoffset(idxs,
                                                self.ranges) + self.ID_offset

        return _gen()

    def __len__(self):
        return self.N

    def __contains__(self, ID):
        return 1 <= (ID - self.ID_offset) <= len(self)

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

    def to_indices(self, ID):
        if ID in self:
            return self.varoffset_to_indices(ID - self.ID_offset, self.ranges)
        else:
            raise ValueError('Index out of range')

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

    @staticmethod
    def indices_to_varoffset(idxs, ranges):
        """Convert the indices of a variable into its ID.

        A variable is identified by an integer ID, but if it is one of
        the variables of a group, it has an associate tuple of
        indices. This function convert the indices into the
        corresponding ID. **Beware** that this function assumes the
        variable IDs in this group start from 1. To use it properly
        the ID must be shifted afterward.

        Parameters
        ----------
        idxs : sequences(positive integers)
            the indices of the variable
        ranges : sequence(positive integers)
            the indices ranges for the group of variables

        Returns
        -------
            int

        Raises
        ------
        ValueError
            when the indices are not within the ranges

        """
        weight = 1
        total = 1
        for i, w in zip(idxs[::-1], ranges[::-1]):
            if i > w or i < 1:
                raise ValueError('Index out of range')
            total += (i - 1) * weight
            weight *= w
        return total

    @staticmethod
    def varoffset_to_indices(i, ranges):
        """Convert the ID of a variable into an index sequence.

        A variable is identified by an integer ID, but if it is one of
        the variables of a group, it has an associate tuple of
        indices. This function convert the ID into the corresponding
        indices. **Beware** that this function assumes the variable
        IDs in this group start from 1. To use it properly an ID must
        be shifted beforehand.

        Parameters
        ----------
        i : positive integer
            the ID of the variable
        ranges : sequence(positive integers)
            the indices ranges for the group of variables

        Returns
        -------
            sequence(positive integers)

        Raises
        ------
        ValueError
            when the ID is not within the appropriate interval

        Examples
        --------
        >>> VariablesGroup.varoffset_to_indices(1,[3,5,4,3])
        [1, 1, 1, 1]
        >>> VariablesGroup.varoffset_to_indices(5,[3,5,4,3])
        [1, 1, 2, 2]
        >>> VariablesGroup.varoffset_to_indices(179,[3,5,4,3])
        [3, 5, 4, 2]
        >>> VariablesGroup.varoffset_to_indices(180,[3,5,4,3])
        [3, 5, 4, 3]
        """
        indices = []
        weights = [1]
        for w in ranges[:0:-1]:
            weights.insert(0, w * weights[0])
        iprime = i - 1
        for w in weights:
            indices.append(iprime // w + 1)
            iprime = iprime % w
        return indices


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

    new_variables(*ranges,label=''):
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
    >>> Zs = V.new_variables(2,3,label='z_{{{},{}}}')
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
        if len(self.groups) == 0:
            last = 0
        else:
            last = self.groups[-1]
        self.groups.append(last + 1)

        newvar = self.groups[-1]
        self.info[newvar] = label
        return newvar

    def new_variables(self, *ranges, label=None):
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
        VariablesGroup, the new variable group

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
        if len(ranges) == 0:
            raise ValueError('There must be at least an index')

        for R in ranges:
            if R <= 0:
                raise ValueError('Ranges should be positive')
        try:
            label.format(*ranges)
        except IndexError:
            raise ValueError(
                'label must be a valid format string for all indices')

        if len(self.groups) == 0:
            start = 1
        else:
            start = self.groups[-1] + 1

        newgroup = VariablesGroup(start, ranges, label)

        self.groups.append(start + len(newgroup) - 1)
        self.info[self.groups[-1]] = newgroup

        return newgroup

    def __len__(self):
        return self.groups[-1]

    def vars(self):
        """Enumerate variables IDs
        """
        return range(1, len(self) + 1)

    def varnames(self):
        """Enumerate variable names

        Generator enumerates all variables by name.
        """
        previous = 0
        for x in self.groups:
            if x == previous + 1:
                yield self.info[x]
            else:
                group = self.info[x]
                for idxs in group.indices():
                    yield group.label(*idxs)
            previous = x
