from cnfformula import CNF

# Returns True/False/undefined
def evaluate_clause(clause, assignment):
    undef = False
    for (polarity, variable) in clause:
        if variable in assignment:
            if (assignment[variable]==polarity) : return True
        else:
            undef = True
    if (undef) : return None
    return False


# Returns a tuple (satisfied, falsified, undefined)
def evaluate_cnf(CNF, assignment):
    return (
        [c for c in CNF if evaluate_clause(c,assignment) is True],
        [c for c in CNF if evaluate_clause(c,assignment) is False],
        [c for c in CNF if evaluate_clause(c,assignment) is None],
    )
