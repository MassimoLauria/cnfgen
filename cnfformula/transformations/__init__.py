#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Package containing formula transformations
"""


__cnf_transformation_mark = "_is_cnf_transformation" 

def register_cnf_transformation(func):
    """Register the function as a formula generator

    This function decorator is used to declare that the function is
    indeed a formula transformation.

    Parameters
    ----------
    func :
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
    setattr(func,__cnf_transformation_mark,True)
    return func


def is_cnf_transformation(func):
    """Test whether the object is a registered formula generator

    Parameters
    ----------
    func : a callable argument
        the function to be registered.

    Returns
    -------
    bool
    """
    return hasattr(func,__cnf_transformation_mark)
