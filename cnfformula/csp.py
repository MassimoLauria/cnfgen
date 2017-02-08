from cnf import CNF
from opb import OPB

class CSP(object):
    """Factory for Constraint Satisfiability Problems
        
    Upon instantiation, this class mutates itself into a class that
    can store and work with constraints of the same type as the output
    format. The output format is specified globally using `set_format`.
    """

    _formats = {'dimacs': CNF, 'latex': CNF, 'opb': OPB}
    _factoryformat = CNF

    def __init__(self):
        self.__class__ = CSP._factoryformat
        CSP._factoryformat.__init__(self)

    @classmethod
    def set_format(cls,output):
        CSP._factoryformat = CSP._formats[output]
