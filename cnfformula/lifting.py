#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function
from .cnf import CNF,parity_constraint

from itertools import product,combinations,permutations


###
### Lifted CNFs
###

class Lift(CNF):
    """Lifted formula

    A formula is made harder by the process of lifting.
    """

    def __init__(self, cnf,rank=1):
        """Build a new CNF with by lifing the old CNF

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

        # Lift all possible literals
        for i in range(1,len(variablenames)):
            varadditional[i] =self.lift_variable_preamble(variablenames[i])
            substitutions[i] =self.lift_a_literal(True, variablenames[i])
            substitutions[-i]=self.lift_a_literal(False,variablenames[i])


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
        clauses=self._orig_cnf._clauses

        # dictionary of comments
        commentlines=dict()
        for (i,c) in self._orig_cnf._comments:
            commentlines.setdefault(i,[]).append(c)


        for i in xrange(len(clauses)):

            # add comments if necessary
            if i in commentlines:
                for comment in commentlines[i]:
                    self._comments.append((len(self._clauses),comment))

            # a substituted clause is the OR of the substituted literals
            domains=[ substitutions[lit] for lit in clauses[i] ]
            domains=tuple(domains)

            block = [ tuple([lit for clause in clause_tuple
                                 for lit in clause ])
                      for clause_tuple in product(*domains)]

            self._add_compressed_clauses(block)

        # lifting may need additional clauses per variables
        # added here so that the comment order is coherent
        for i,block in enumerate(varadditional[1:],1):
            if block:
                self._comments.append((len(self._clauses),
                                       "Clauses for lifted variable {}".format(variablenames[i])))
                self._add_compressed_clauses(block)
         
        # add trailing comments
        if len(clauses) in commentlines:
            for comment in commentlines[len(clauses)]:
                self._comments.append((len(self._clauses),comment))

        assert self._orig_cnf._check_coherence()
        assert self._check_coherence()

    def lift_variable_preamble(self, name):
        """Additional clauses for each lifted variable

        Arguments:
        - `name`:     variable to be substituted

        Returns: a list of clauses
        """
        return []


    def lift_a_literal(self, polarity, name):
        """Substitute a literal with the lifting function

        Arguments:
        - `polarity`: polarity of the literal
        - `name`:     variable to be substituted

        Returns: a list of clauses
        """
        return [ [ (polarity,name) ] ]



class IfThenElse(Lift):
    """Lifted formula: substitutes variable with a three variables
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

        Lift.__init__(self,cnf)

        self._header="If-Then-Else substituted formula\n\n".format(self._rank) \
            +self._header

    def lift_a_literal(self, polarity,varname):
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


class Majority(Lift):
    """Lifted formula: substitutes variable with a Majority
    """
    def __init__(self, cnf, rank):
        """Build a new CNF obtained by substituting a Majority to the
        variables of the original CNF

        Arguments:
        - `cnf`: the original cnf
        - `rank`: how many variables in each or
        """
        self._rank = rank

        Lift.__init__(self,cnf)

        self._header="Majority {} substituted formula\n\n".format(self._rank) \
            +self._header

    def lift_a_literal(self, polarity,varname):
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


class InnerOr(Lift):
    """Lifted formula: substitutes variable with a OR
    """
    def __init__(self, cnf, rank):
        """Build a new CNF obtained by substituting a OR to the
        variables of the original CNF

        Arguments:
        - `cnf`: the original cnf
        - `rank`: how many variables in each or
        """
        self._rank = rank

        Lift.__init__(self,cnf)

        self._header="OR {} substituted formula\n\n".format(self._rank) \
            +self._header

    def lift_a_literal(self, polarity,varname):
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


class Equality(Lift):
    """Lifted formula: substitutes variable with 'all equals'
    """
    def __init__(self, cnf, rank):
        """Build a new CNF obtained by substituting 'all equals' to the
        variables of the original CNF

        Arguments:
        - `cnf`: the original cnf
        - `rank`: how many variables in each or
        """
        self._rank = rank

        Lift.__init__(self,cnf)

        self._header="EQ {} substituted formula\n\n".format(self._rank) \
            +self._header

    def lift_a_literal(self, polarity,varname):
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


class InnerXor(Lift):
    """Lifted formula: substitutes variable with a XOR
    """
    def __init__(self, cnf, rank):
        """Build a new CNF obtained by substituting a XOR to the
        variables of the original CNF

        Arguments:
        - `cnf`: the original cnf
        - `rank`: how many variables in each xor
        """
        self._rank = rank

        Lift.__init__(self,cnf)

        self._header="XOR {} substituted formula\n\n".format(self._rank) \
            +self._header

    def lift_a_literal(self, polarity,varname):
        """Substitute a literal with a (negated) XOR

        Arguments:
        - `polarity`: polarity of the literal
        - `varname`: fariable to be substituted

        Returns: a list of clauses
        """
        names = [ "{{{}}}^{}".format(varname,i) for i in range(self._rank) ]
        return parity_constraint(names,polarity)


class Selection(Lift):
    """Lifted formula: Y variable select X values
    """
    def __init__(self, cnf, rank):
        """Build a new CNF obtained by lifting procedures

        Arguments:
        - `cnf`: the original cnf
        - `rank`: how many variables in each xor
        """
        self._rank = rank

        Lift.__init__(self,cnf)

        self._header="Formula lifted by selectors over {} values\n\n".format(self._rank) \
            +self._header


    def lift_variable_preamble(self, name):
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


    def lift_a_literal(self, polarity,varname):
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

class One(Lift):
    """Lifted formula: exactly one variable is true
    """
    def __init__(self, cnf, rank):
        """Build a new CNF obtained by lifting procedures

        Arguments:
        - `cnf`: the original cnf
        - `rank`: how many variables in each substitution
        """
        self._rank = rank

        Lift.__init__(self,cnf)

        self._header="Formula lifted by \"exactly one\""+ \
                     " substitution over {} values\n\n".format(self._rank) \
                     +self._header

    def lift_a_literal(self, polarity,varname):
        """Substitute a literal with a (negated) XOR

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

    # lifting name : ("help description", function, default rank)

    'none': ("leaves the formula alone", Lift,1),
    'or'  : ("OR substitution     (default rank: 2)", InnerOr,2),
    'xor' : ("XOR substitution    (default rank: 2)", InnerXor,2),
    'sel' : ("selection lifting   (default rank: 3)", Selection,3),
    'eq'  : ("all variables equal (default rank: 3)", Equality,3),
    'ite' : ("if x then y else z  (rank ignored)",    IfThenElse,3),
    'maj' : ("Loose majority      (default rank: 3)", Majority,3),
    'one' : ("Exactly one         (default rank: 3)", One,3)    
    }


def LiftFormula(cnf,lift_method,lift_rank=None):
    """Lift a formula using one of the known methods
    
    Arguments:
    - `cnf`: the formula to be lifted
    - `lift_method`: a string naming the lift method
    - `lift_rank`: the rank of the lift method
    """
    implemented_lifting=available()
    if not lift_method in implemented_lifting:
        raise ValueError("There is no implementation for lifting method {}".format(lift_method))
    
    method=implemented_lifting[lift_method][1]
    rank=lift_rank or implemented_lifting[lift_method][2]

    return method(cnf,rank)


