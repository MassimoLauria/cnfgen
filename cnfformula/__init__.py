#!/usr/bin/env python

from cnfformula.cnf import CNF
from cnfformula.transformation import TransformFormula
from cnfformula.transformation import available as available_transform


__all__ = ["CNF","TransformFormula","available_transform"]


def load_formula_generators():
    """Load CNF generators from `cnfformula.families`.

    This code explores the submodules of `cnfformula.families` and
    load the formula generators, or at least the objects marked as
    such with the `cnfformula.families.register_cnf_generator`
    function decorator.
    """
    
    import pkgutil
    import sys
    from .families import __path__ as bpath
    from .families import __name__ as bname
    from .families import is_cnf_generator
    
    loot = {}
    
    for loader, module_name, _ in  pkgutil.walk_packages(bpath):
        module_name = bname+"."+module_name
        module = loader.find_module(module_name).load_module(module_name)
        for objname in dir(module):
            obj = getattr(module, objname)
            if is_cnf_generator(obj):
                loot[objname] = obj

    # Load the formula generators in the `cnfformula` namespace
    self_ref = sys.modules[__name__]
    self_ref.__dict__.update(loot)
    __all__.extend(name for name in loot.keys() if name not in __all__)


# do the actual loading
load_formula_generators()

