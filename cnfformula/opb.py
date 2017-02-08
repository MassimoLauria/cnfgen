from __future__ import print_function

from cnf import CNF

class OPB(CNF):
    def __init__(self):
        self._constraints = []
        self.add_clause_unsafe = self.add_constraint
        self.add_clause = self.add_constraint
        CNF.__init__(self)

    def dimacs(self, export_header=False, extra_text=None):
        from cStringIO import StringIO
        output = StringIO()
        output.write("* #variable= {} #constraint= {}\n".format(
            len(self._index2name),len(self._constraints)))
        for c in self._constraints:
            freeterm = c[-1]
            for term in c[:-1]:
                coefficient = term[0]
                literal = "x" + str(self._name2index[term[2]]+1)
                if not term[1] :
                    coefficient *= -1
                    freeterm += coefficient
                    # literal = "~" + literal
                output.write("{} {} ".format(coefficient,literal))
            output.write(">= {} ;\n".format(freeterm))

        return output.getvalue()
        
    def add_constraint(self, constraint, strict=False):
        freeterm = constraint[-1]
        if isinstance(freeterm,tuple):
            # Got a disjunction
            constraint = [(1,)+lit for lit in constraint] + [1]
        self._constraints.append(constraint)

    @classmethod
    def _inequality_constraint_builder(cls, variables, k, greater=False):
        if greater:
            yield [(1,True,var) for var in variables] + [k+1]
        else:
            yield [(-1,True,var) for var in variables] + [-k+1]
