#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function

from ..cnf import CNF
from ..cnf import parity_constraint

from ..cmdline  import register_cnf_transformation_subcommand
from ..transformations import register_cnf_transformation

from itertools import combinations,product,permutations

###
### Substitions
###

class BaseSubstitution(CNF):
    """Apply a substitution to a formula
    """

    def __init__(self, cnf):
        """Build a new CNF substituting variables

        Arguments:
        - `cnf`: the original cnf
        """
        assert cnf._coherent
        self._orig_cnf = cnf
        super(BaseSubstitution,self).__init__([],header=cnf._header)

        # Load original variable names
        #
        # For n variables we get
        #
        # varadditional = [None, F1, F2,..., Fn]
        # substitution  = [None, F1, F2,..., Fn, -Fn, -F(n-1), ..., -F2, -F1]
        #
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


@register_cnf_transformation
class IfThenElseSubstitution(BaseSubstitution):
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

        super(IfThenElseSubstitution,self).__init__(cnf)

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


@register_cnf_transformation
class MajoritySubstitution(BaseSubstitution):
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

        super(MajoritySubstitution,self).__init__(cnf)

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


@register_cnf_transformation
class OrSubstitution(BaseSubstitution):
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

        super(OrSubstitution,self).__init__(cnf)

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


@register_cnf_transformation
class AllEqualSubstitution(BaseSubstitution):
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

        super(AllEqualSubstitution,self).__init__(cnf)

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

@register_cnf_transformation
class NotAllEqualSubstitution(AllEqualSubstitution):
    """Transformed formula: substitutes variable with 'not all equals'
    """
    def __init__(self, cnf, rank):
        """Build a new CNF obtained by substituting 'not all equals' to the
        variables of the original CNF

        Arguments:
        - `cnf`: the original cnf
        - `rank`: how many variables in each or
        """
        super(NotAllEqualSubstitution,self).__init__(cnf,rank)

        self._header="N"+self._header

    def transform_a_literal(self, polarity,varname):
        """Substitute a positive literal with an 'not all equal' statement,

        Arguments:
        - `polarity`: polarity of the literal
        - `varname`: fariable to be substituted

        Returns: a list of clauses
        """
        return AllEqualSubstitution.transform_a_literal(self,not polarity,varname)

@register_cnf_transformation
class XorSubstitution(BaseSubstitution):
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

        super(XorSubstitution,self).__init__(cnf)

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

@register_cnf_transformation
class FormulaLifting(BaseSubstitution):
    """Formula lifting: Y variable select X values
    """
    def __init__(self, cnf, rank):
        """Build a new CNF obtained by lifting procedures

        Arguments:
        - `cnf`: the original cnf
        - `rank`: how many variables in each xor
        """
        self._rank = rank

        super(FormulaLifting,self).__init__(cnf)

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


@register_cnf_transformation
class ExactlyOneSubstitution(BaseSubstitution):
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

        super(ExactlyOneSubstitution,self).__init__(cnf)

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


#
# Command line helpers for these substitutions
#
@register_cnf_transformation_subcommand
class NoSubstitutionCmd:
    name='none'
    description='no transformation'

    @staticmethod
    def setup_command_line(parser):
        pass

    @staticmethod
    def transform_cnf(F,args):
        return F

@register_cnf_transformation_subcommand
class OrSubstitutionCmd:
    name='or'
    description='substitute variable x with OR(x1,x2,...,xN)'

    @staticmethod
    def setup_command_line(parser):
        parser.add_argument('N',type=int,nargs='?',default=2,action='store',help="arity (default: 2)")

    @staticmethod
    def transform_cnf(F,args):
        return  OrSubstitution(F,args.N)

@register_cnf_transformation_subcommand
class XorSubstitutionCmd:
    name='xor'
    description='substitute variable x with XOR(x1,x2,...,xN)'

    @staticmethod
    def setup_command_line(parser):
        parser.add_argument('N',type=int,nargs='?',default=2,action='store',help="arity (default: 2)")

    @staticmethod
    def transform_cnf(F,args):
        return  XorSubstitution(F,args.N)

@register_cnf_transformation_subcommand
class AllEqualsSubstitutionCmd:
    name='eq'
    description='substitute variable x with predicate x1==x2==...==xN (i.e. all equals)'

    @staticmethod
    def setup_command_line(parser):
        parser.add_argument('N',type=int,nargs='?',default=2,action='store',help="arity (default: 3)")

    @staticmethod
    def transform_cnf(F,args):
        return  AllEqualSubstitution(F,args.N)

@register_cnf_transformation_subcommand
class NeqSubstitutionCmd:
    name='neq'
    description='substitute variable x with predicate |{x1,x2,...,xN}|>1 (i.e. not all equals)'

    @staticmethod
    def setup_command_line(parser):
        parser.add_argument('N',type=int,nargs='?',default=2,action='store',help="arity (default: 3)")

    @staticmethod
    def transform_cnf(F,args):
        return  NotAllEqualSubstitution(F,args.N)

@register_cnf_transformation_subcommand
class MajSubstitution:
    name='maj'
    description='substitute variable x with predicate Majority(x1,x2,...,xN)'

    @staticmethod
    def setup_command_line(parser):
        parser.add_argument('N',type=int,nargs='?',default=2,action='store',help="arity (default: 3)")

    @staticmethod
    def transform_cnf(F,args):
        return  MajoritySubstitution(F,args.N)

@register_cnf_transformation_subcommand
class IfThenElseSubstitutionCmd:
    name='ite'
    description='substitute variable x with predicate "if X then Y else Z"'

    @staticmethod
    def setup_command_line(parser):
        pass
    
    @staticmethod
    def transform_cnf(F,args):
        return  IfThenElseSubstitution(F)

@register_cnf_transformation_subcommand
class ExactlyOneSubstitutionCmd:
    name='one'
    description='substitute variable x with predicate x1+x2+...+xN = 1'

    @staticmethod
    def setup_command_line(parser):
        parser.add_argument('N',type=int,nargs='?',default=2,action='store',help="arity (default: 3)")
    
    @staticmethod
    def transform_cnf(F,args):
        return  ExactlyOneSubstitution(F,args.N)



# Technically lifting is not a substitution, therefore it should be in
# another file. Unfortunately there is a lot of dependency from
# this one.
@register_cnf_transformation_subcommand
class FormulaLiftingCmd:
    """Lifting 
    """
    name='lift'
    description='one dimensional lifting  x -->  x1 y1  OR ... OR xN yN, with y1+..+yN = 1'

    @staticmethod
    def setup_command_line(parser):
        parser.add_argument('N',type=int,nargs='?',default=2,action='store',help="arity (default: 3)")
    
    @staticmethod
    def transform_cnf(F,args):
        return FormulaLifting(F,args.N)


