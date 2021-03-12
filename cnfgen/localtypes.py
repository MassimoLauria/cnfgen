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
    invalid_type = False
    try:
        for v in value:
            if not isinstance(v, numbers.Integral):
                invalid_type = True
    except TypeError:
        invalid_type = True
    if invalid_type:
        raise TypeError(msg)
    for v in value:
        if v < 1:
            raise ValueError(msg)

def non_negative_int_seq(value, name):
    """Check that `value` is a positive integer"""
    msg = "argument '{}' must be a sequence of non negative integers".format(name)
    invalid_type = False
    try:
        for v in value:
            if not isinstance(v, numbers.Integral):
                invalid_type = True
    except TypeError:
        invalid_type = True
    if invalid_type:
        raise TypeError(msg)
    for v in value:
        if v < 0:
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
