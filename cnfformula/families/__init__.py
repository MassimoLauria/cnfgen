#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Formula families useful in proof complexity
"""


__cnf_generator_mark = "_is_cnf_generator" 

def register_cnf_generator(func):
    """Register the fucntion as a formula generator

    This function decorator is used to declare that the function is
    indeed a formula generator. In this way the fucntion becomes
    accessible directly from `cnfformua.families` package.

    Parameters
    ----------
    func : a callable argument
        the function to be registered.

    Returns
    -------
    None

    Raises
    ------
    AssertionError 
        when the argument is not a function
    """
    assert callable(func)
    setattr(func,__cnf_generator_mark,True)
    return func


def is_cnf_generator(func):
    """Test whether the object is a registered formula generator

    Parameters
    ----------
    func : a callable argument
        the function to be registered.

    Returns
    -------
    bool
    """
    return hasattr(func,__cnf_generator_mark)
