#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Functions to check the arguments types
"""

import numbers


def positive_int(value, name):
    """Check that `value` is a positive integer"""
    msg = "argument '{}' must be a positive integer".format(name)
    if not isinstance(value, numbers.Integral):
        raise TypeError(msg)
    if value < 1:
        raise ValueError(msg)

def positive_int_seq(value, name):
    """Check that `value` is a positive integer"""
    msg = "argument '{}' must be a sequence of positive integers".format(name)
    try:
        for v in value:
            if not isinstance(v, numbers.Integral):
                raise TypeError('non numeric element in the sequence')
    except TypeError as te:
        raise TypeError(msg) from te

    for v in value:
        if v < 1:
            raise ValueError(msg)

def non_negative_int_seq(value, name):
    """Check that `value` is a positive integer"""
    msg = "argument '{}' must be a sequence of non negative integers".format(name)
    try:
        for v in value:
            if not isinstance(v, numbers.Integral):
                raise TypeError('non numeric element in the sequence')
    except TypeError as te:
        raise TypeError(msg) from te

    for v in value:
        if v < 0:
            raise ValueError(msg)

def one_of_values(value, name, choices):
    '''Check if the value is in a specific set'''
    msg = "argument '{}' must be one of [{}]".format(name,
                                                     choices)
    if value not in choices:
        raise ValueError(msg)

def any_int(value, name):
    """Check that `value` is an integer"""
    msg = "argument '{}' must be have integer value".format(name)
    if not isinstance(value, numbers.Integral):
        raise TypeError(msg)

def non_negative_int(value, name):
    """Check that the `value` is a non negative"""
    msg = "argument '{}' must be a non negative integer".format(name)
    if not isinstance(value, numbers.Integral):
        raise TypeError(msg)
    if value < 0:
        raise ValueError(msg)


def probability_value(value, name):
    """Check that the `value` is a real between 0 and 1"""
    msg = "argument '{}' must be a real between 0 and 1".format(name)
    if not isinstance(value, numbers.Real):
        raise TypeError(msg)
    if value < 0 or value > 1:
        raise ValueError(msg)
