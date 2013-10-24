#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function
from .cnf import CNF,parity_constraint

from itertools import product,combinations,permutations

#
# Transformation of a list of clauses
#
class StopClauses(StopIteration):
    """Exception raised when an iterator of clauses finish.

    Attributes:
        variables -- number of variables in the clause stream
        clauses   -- number of clauses streamed
    """
    def __init__(self, variables, clauses):
        self.variables = variables
        self.clauses = clauses


def transform_compressed_clauses(clauses,method='none',rank=None):
    """
    Build a new CNF with by appling a transformation the old CNF. It
    works on the compressed representation of a CNF: both input and
    output of this transformation is a list of tuples of literals
    represented as integer.

    E.g. [(-1,2,3), (-2,1,5), (3,4,5)]

    Arguments:
    - `clauses`: a sequence of clause in DIMACS format
    """

    # Use a dummy lifting operation to get information about the
    # lifting structure.
    poslift=None
    neglift=None
    
    dummycnf=CNF([[(True, "x")]])
    dummycnf=TransformFormula(dummycnf,method,rank)

    varlift    =dummycnf.transform_variable_preamble("x")
    poslift    =dummycnf.transform_a_literal(True,"x")
    neglift    =dummycnf.transform_a_literal(False,"x")

    varlift    = [list(dummycnf._compress_clause(cls)) for cls in varlift ]
    poslift    = [list(dummycnf._compress_clause(cls)) for cls in poslift ]
    neglift    = [list(dummycnf._compress_clause(cls)) for cls in neglift ]
    offset     = len(list(dummycnf.variables()))

    # information about the input formula
    input_variables = 0

    output_clauses   = 0
    output_variables = 0

    def substitute(literal):
        if literal>0:
            var=literal
            lift=poslift
        else:
            var=-literal
            lift=neglift

        substitute.max=max(var,substitute.max)
        return [[ (l/abs(l))*offset*(var-1)+l for l in cls ] for cls in lift]

    substitute.max=0
           
    for cls in clauses:

        # a substituted clause is the OR of the substituted literals
        domains=[ substitute(lit) for lit in cls ]
        domains=tuple(domains)

        for clause_tuple in product(*domains):
            output_clauses +=1
            yield [lit for clause in clause_tuple for lit in clause ]

    # count the variables
    input_variables  = substitute.max
    output_variables = input_variables*offset

    for i in xrange(input_variables):
        for cls in varlift:
            output_clauses += 1
            yield [ (l/abs(l))*offset*i+l for l in cls ]

    raise StopClauses(output_variables,output_clauses)


###
### Transformation of CNFs
###

class TransformedCNF(CNF):
    """Transformed formula

    A formula is modified (usually made harder).
    """

    def __init__(self, cnf,rank=1):
        """Build a new CNF with by maniputation of the old CNF

        Arguments:
        - `cnf`: the original cnf
        """
        assert cnf._coherent
        self._orig_cnf = cnf
        CNF.__init__(self,[],header=cnf._header)

        # Load original variable names
        variablenames = [None]+list(self._orig_cnf.variables())
        substitutions = [None]*(2*len(variablenames)-1)
        varadditional = [None]*(len(variablenames))

        # Transform all possible literals
        for i in range(1,len(variablenames)):
            varadditional[i] =self.transform_variable_preamble(variablenames[i])
            substitutions[i] =self.transform_a_literal(True, variablenames[i])
            substitutions[-i]=self.transform_a_literal(False,variablenames[i])


        # Collect new variable names from the CNFs:
        # clause compression needs the variable names
        for i in range(1,len(variablenames)):
            for clause in varadditional[i]+\
                          substitutions[i]+\
                          substitutions[-i]:
                for _,varname in clause:
                    self.add_variable(varname)

         

        # Compress substitution cnfs
        for i in range(1,len(varadditional)):
            varadditional[i] =[list(self._compress_clause(cls))
                               for cls in varadditional[i] ]

        for i in range(1,len(substitutions)):
            substitutions[i] =[list(self._compress_clause(cls))
                               for cls in substitutions[i] ]

        # build and add new clauses
        for orig_cls in self._orig_cnf._clauses:

            # a substituted clause is the OR of the substituted literals
            domains=[ substitutions[lit] for lit in orig_cls ]
            domains=tuple(domains)

            block = [ tuple([lit for clause in clause_tuple
                                 for lit in clause ])
                      for clause_tuple in product(*domains)]

            self._add_compressed_clauses(block)

        # transformation may need additional clauses per variables
        for block in varadditional[1:]:
            if block:
                self._add_compressed_clauses(block)
         
        assert self._orig_cnf._check_coherence()
        assert self._check_coherence()

    def transform_variable_preamble(self, name):
        """Additional clauses for each variable

        Arguments:
        - `name`:     variable to add clauses for

        Returns: a list of clauses
        """
        return []


    def transform_a_literal(self, polarity, name):
        """Substitute a literal with the transformation function

        Arguments:
        - `polarity`: polarity of the literal
        - `name`:     variable to be substituted

        Returns: a list of clauses
        """
        return [ [ (polarity,name) ] ]



class IfThenElse(TransformedCNF):
    """Transformed formula: substitutes variable with a three variables
    if-then-else
    """
    def __init__(self, cnf, rank=1):
        """Build a new CNF obtained by substituting an if-then-else to the
        variables of the original CNF

        Arguments:
        - `cnf`: the original cnf
        - `rank`: ignored
        """
        self._rank = rank

        TransformedCNF.__init__(self,cnf)

        self._header="If-Then-Else substituted formula\n\n".format(self._rank) \
            +self._header

    def transform_a_literal(self, polarity,varname):
        """Substitute a positive literal with an if then else statement,

        Arguments:
        - `polarity`: polarity of the literal
        - `varname`: variable to be substituted

        Returns: a list of clauses
        """
        X = "{{{}}}^0".format(varname)
        Y = "{{{}}}^1".format(varname)
        Z = "{{{}}}^2".format(varname)

        return [ [ (False,X) , (polarity,Y) ] , [ (True, X) , (polarity,Z) ] ]


class Majority(TransformedCNF):
    """Transformed formula: substitutes variable with a Majority
    """
    def __init__(self, cnf, rank):
        """Build a new CNF obtained by substituting a Majority to the
        variables of the original CNF

        Arguments:
        - `cnf`: the original cnf
        - `rank`: how many variables in each or
        """
        self._rank = rank

        TransformedCNF.__init__(self,cnf)

        self._header="Majority {} substituted formula\n\n".format(self._rank) \
            +self._header

    def transform_a_literal(self, polarity,varname):
        """Substitute a positive literal with Loose Majority,
        and negative literals with Strict Minority.

        Arguments:
        - `polarity`: polarity of the literal
        - `varname`: fariable to be substituted

        Returns: a list of clauses
        """

        # Majority is espressed as a set of positive clauses,
        # while Minority as a set on negative ones
        lit = [ (polarity,"{{{}}}^{}".format(varname,i)) for i in range(self._rank) ]

        if polarity:
            witness = self._rank // 2 + 1   # avoid strict majority of 'False'
        else:
            witness = (self._rank + 1) // 2 # avoid loose  majority of 'True'

        binom = combinations

        return [ s for s in binom(lit,witness) ]


class InnerOr(TransformedCNF):
    """Transformed formula: substitutes variable with a OR
    """
    def __init__(self, cnf, rank):
        """Build a new CNF obtained by substituting a OR to the
        variables of the original CNF

        Arguments:
        - `cnf`: the original cnf
        - `rank`: how many variables in each or
        """
        self._rank = rank

        TransformedCNF.__init__(self,cnf)

        self._header="OR {} substituted formula\n\n".format(self._rank) \
            +self._header

    def transform_a_literal(self, polarity,varname):
        """Substitute a positive literal with an OR,
        and negative literals with its negation.

        Arguments:
        - `polarity`: polarity of the literal
        - `varname`: fariable to be substituted

        Returns: a list of clauses
        """
        names = [ "{{{}}}^{}".format(varname,i) for i in range(self._rank) ]
        if polarity:
            return [[ (True,name) for name in names ]]
        else:
            return [ [(False,name)] for name in names ]


class Equality(TransformedCNF):
    """Transformed formula: substitutes variable with 'all equals'
    """
    def __init__(self, cnf, rank):
        """Build a new CNF obtained by substituting 'all equals' to the
        variables of the original CNF

        Arguments:
        - `cnf`: the original cnf
        - `rank`: how many variables in each or
        """
        self._rank = rank

        TransformedCNF.__init__(self,cnf)

        self._header="EQ {} substituted formula\n\n".format(self._rank) \
            +self._header

    def transform_a_literal(self, polarity,varname):
        """Substitute a positive literal with an 'all equal' statement,

        Arguments:
        - `polarity`: polarity of the literal
        - `varname`: fariable to be substituted

        Returns: a list of clauses
        """
        names = [ "{{{}}}^{}".format(varname,i) for i in range(self._rank) ]
        pairs = permutations(names,2)
        if polarity:
            return [ [ (False,a) , (True,b) ] for a,b in pairs ] # a true variable implies all the others to true.

        else:
            return [[ (False,a) for a in names ] , [ (True,a) for a in names ] ] # at least a true and a false variable.

class NonEquality(Equality):
    """Transformed formula: substitutes variable with 'not all equals'
    """
    def __init__(self, cnf, rank):
        """Build a new CNF obtained by substituting 'not all equals' to the
        variables of the original CNF

        Arguments:
        - `cnf`: the original cnf
        - `rank`: how many variables in each or
        """
        Equality.__init__(self,cnf,rank)

        self._header="N"+self._header

    def transform_a_literal(self, polarity,varname):
        """Substitute a positive literal with an 'not all equal' statement,

        Arguments:
        - `polarity`: polarity of the literal
        - `varname`: fariable to be substituted

        Returns: a list of clauses
        """
        return Equality.transform_a_literal(self,not polarity,varname)

        
class InnerXor(TransformedCNF):
    """Transformed formula: substitutes variable with a XOR
    """
    def __init__(self, cnf, rank):
        """Build a new CNF obtained by substituting a XOR to the
        variables of the original CNF

        Arguments:
        - `cnf`: the original cnf
        - `rank`: how many variables in each xor
        """
        self._rank = rank

        TransformedCNF.__init__(self,cnf)

        self._header="XOR {} substituted formula\n\n".format(self._rank) \
            +self._header

    def transform_a_literal(self, polarity,varname):
        """Substitute a literal with a (negated) XOR

        Arguments:
        - `polarity`: polarity of the literal
        - `varname`: fariable to be substituted

        Returns: a list of clauses
        """
        names = [ "{{{}}}^{}".format(varname,i) for i in range(self._rank) ]
        return parity_constraint(names,polarity)


class Lifting(TransformedCNF):
    """Formula lifting: Y variable select X values
    """
    def __init__(self, cnf, rank):
        """Build a new CNF obtained by lifting procedures

        Arguments:
        - `cnf`: the original cnf
        - `rank`: how many variables in each xor
        """
        self._rank = rank

        TransformedCNF.__init__(self,cnf)

        self._header="Formula with lifting with selectors over {} values\n\n".format(self._rank) \
            +self._header


    def transform_variable_preamble(self, name):
        """Additional clauses for each lifted variable

        Arguments:
        - `name`:     variable to be substituted

        Returns: a list of clauses
        """
        selector_clauses=[]
        selector_clauses.append([ (True,   "Y_{{{}}}^{}".format(name,i)) for i in range(self._rank)])
        
        for s1,s2 in combinations(["Y_{{{}}}^{}".format(name,i) for i in range(self._rank)],2):
                selector_clauses.append([(False,s1),(False,s2)])

        return selector_clauses


    def transform_a_literal(self, polarity,varname):
        """Substitute a literal with a (negated) XOR

        Arguments:
        - `polarity`: polarity of the literal
        - `varname`: fariable to be substituted

        Returns: a list of clauses
        """
        clauses=[]
        for i in range(self._rank):
            clauses.append([ (False,   "Y_{{{}}}^{}".format(varname,i)),
                             (polarity,"X_{{{}}}^{}".format(varname,i)) ])
        return clauses

class One(TransformedCNF):
    """Transformed formula: exactly one variable is true
    """
    def __init__(self, cnf, rank):
        """Build a new CNF obtained substituting all variables with
        'exactly one' function.

        Arguments:
        - `cnf`: the original cnf
        - `rank`: how many variables in each substitution
        """
        self._rank = rank

        TransformedCNF.__init__(self,cnf)

        self._header="Formula transformed by \"exactly one\""+ \
                     " substitution over {} values\n\n".format(self._rank) \
                     +self._header

    def transform_a_literal(self, polarity,varname):
        """Substitute a literal with an \"Exactly One\"

        Arguments:
        - `polarity`: polarity of the literal
        - `varname`: fariable to be substituted

        Returns: a list of clauses
        """
        clauses=[]
        varnames=["X_{{{}}}^{}".format(varname,i) for i in range(self._rank)]
        
        if polarity:
            # at least one variable is true
            clauses.append([ (True,name) for name in varnames ])
            # no two variables are true
            for (n1,n2) in combinations(varnames,2):
                clauses.append([ (False,n1), (False,n2)])
        else:
            # if all variables but one are false, the other must be false
            for name in varnames:
                clauses.append([(False,name)]+
                               [(True,other) for other in varnames if other!=name])
        return clauses



###
### Implemented features
###
def available():
    return {

    # transformation name : ("help description", function, default rank)

    'none': ("leaves the formula alone", TransformedCNF,1),
    'or'  : ("OR substitution     (default rank: 2)", InnerOr,2),
    'xor' : ("XOR substitution    (default rank: 2)", InnerXor,2),
    'lift': ("lifting             (default rank: 3)", Lifting,3),
    'eq'  : ("all variables equal (default rank: 3)", Equality,3),
    'neq' : ("not all vars  equal (default rank: 3)", NonEquality,3),
    'ite' : ("if x then y else z  (rank ignored)",    IfThenElse,3),
    'maj' : ("Loose majority      (default rank: 3)", Majority,3),
    'one' : ("Exactly one         (default rank: 3)", One,3)    
    }


def TransformFormula(cnf,t_method,t_arity=None):
    """Transform a formula using one of the known methods
    
    Arguments:
    - `cnf`: the formula to be transformed
    - `t_method`: a string naming the transformation method
    - `t_rank`: the arity of the transformation method
    """
    implemented_transformations=available()
    if not t_method in implemented_transformations:
        raise ValueError("There is no implementation for transformation {}".format(t_method))
    
    method=implemented_transformations[t_method][1]
    arity=t_arity or implemented_transformations[t_method][2]

    return method(cnf,arity)


