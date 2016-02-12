#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Batches are collections of canonical cnf benchmarks.

The idea is that a batch should produce the same set of formulas regardless of other considerations, 
and in particular it should never use the random seed of the system. The it should exit.
"""

import random

__cnf_batch_mark = "_is_cnf_batch" 

def register_cnf_batch(cls):
    """Register the fucntion as a CNF batch generator

    This class decorator is used to test/declare that the class is
    indeed a CNF batch generator.

    Parameters
    ----------
    cls : any
        the class to test

    Returns
    -------
    None

    Raises
    ------
    AssertionError 
        when the argument is not a function
    """
    assert hasattr(cls,'name') and \
           hasattr(cls,'description') and \
           hasattr(cls,'random_seed') and \
           hasattr(cls,'run') 
    setattr(cls,__cnf_batch_mark,True)
    return cls


def is_cnf_batch(cls):
    """Test whether the object is a registered CNF batch generator

    Parameters
    ----------
    cls : any
        the class to test

    Returns
    -------
    bool
    """
    return hasattr(cls,__cnf_batch_mark)


def find_formula_batches():
    """Look in cnfformula.batches package for implementations of CNF batches"""
    
    import pkgutil

    result = []
    
    for loader, module_name, _ in  pkgutil.walk_packages(__path__):
        module_name = __name__+"."+module_name
        module = loader.find_module(module_name).load_module(module_name)
        for objname in dir(module):
            obj = getattr(module, objname)
            if is_cnf_batch(obj):
                result.append(obj)
    result.sort(key=lambda x: x.name)
    return result

def run(args):
    """Run the appropriate CNF batch generator"""
    
    old_rng_state = random.getstate()

    collection = [ obj for obj in find_formula_batches() if obj.name == args.collection ]
                   
    if len(collection) == 0:
        raise ValueError("No collection of CNFs with that name.")

    if len(collection) > 1:
        raise RuntimeError("[Internal Error] Multiple collections of CNFs with the same name.")

    # Run the generator
    collection[0].run()
    
    random.setstate(old_rng_state)

    return
