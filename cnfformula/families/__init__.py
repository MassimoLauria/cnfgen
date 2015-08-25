#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Formula families useful in proof complexity

Copyright (C) 2012, 2013, 2014, 2015  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git
"""




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

    """
    assert callable(func)
    print "Register %s"%func.__name__
    setattr(func,"_CNFGenerator",True)
    return func



###
### Automatically explore the submodules and load the formula families
### implementations in the module namespace.
###

def find_formula_generators():
    """Look in cnfformula.families package for implementations of CNFs"""

    import pkgutil

    result = []
    
    for loader, module_name, _ in  pkgutil.walk_packages(__path__):
        module_name = __name__+"."+module_name
        module = loader.find_module(module_name).load_module(module_name)
        print module 
        print module_name
        for objname in dir(module):
            obj = getattr(module, objname)
            print obj
            if hasattr(obj,"_CNFgenerator"):
                result.append(obj)
    result.sort(key=lambda x: x.name)
    return result


from .pigeonhole import PigeonholePrinciple,GraphPigeonholePrinciple
from .graphisomorphism import GraphIsomorphism, GraphAutomorphism
from .pebbling import PebblingFormula, StoneFormula
from .counting import PerfectMatchingPrinciple, CountingPrinciple
from .ordering import OrderingPrinciple,GraphOrderingPrinciple
from .tseitin  import TseitinFormula
from .subsetcardinality import SubsetCardinalityFormula
from .subgraph import SubgraphFormula,CliqueFormula,RamseyWitnessFormula
from .coloring import GraphColoringFormula,EvenColoringFormula
from .randomformulas import RandomKCNF
from .ramsey import RamseyLowerBoundFormula


__all__ = ["PigeonholePrinciple",
           "GraphPigeonholePrinciple",
           "PebblingFormula",
           "StoneFormula",
           "OrderingPrinciple",
           "GraphOrderingPrinciple",
           "GraphIsomorphism",
           "GraphAutomorphism",
           "RamseyLowerBoundFormula",
           "SubsetCardinalityFormula",
           "TseitinFormula",
           "PerfectMatchingPrinciple",
           "CountingPrinciple",
           "GraphColoringFormula",
           "EvenColoringFormula",
           "SubgraphFormula",
           "CliqueFormula",
           "RamseyWitnessFormula",
           "RandomKCNF"]
