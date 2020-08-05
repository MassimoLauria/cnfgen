import random


def stableshuffle(inputfile,
                  outputfile,
                  variable_permutation=None,
                  clause_permutation=None,
                  polarity_flip=None):

    subst = None
    line_counter = 0
    clause_counter = 0

    for l in inputfile.readlines():

        line_counter += 1

        # discard header
        if l[0] == 'c':
            continue

        # parse spec line
        if l[0] == 'p':
            if subst:
                raise ValueError("Syntax error: " +
                                 "line {} contains a second spec line.".format(
                                     line_counter))
            _, _, nstr, mstr = l.split()
            n = int(nstr)
            subst = substitution(n, variable_permutation, polarity_flip)
            m = int(mstr)

            # Clause permutation
            if clause_permutation == None:
                clause_permutation = list(range(m))
                random.shuffle(clause_permutation)

            clause_buffer = [None] * m

            print(l, end='', file=outputfile)

            continue

        # parse literals
        clause = [int(lit) for lit in l.split()]

        # Checks at the end of clause
        if clause[-1] != 0:
            raise ValueError("Syntax error: last clause was incomplete")

        clause_buffer[clause_permutation[clause_counter]] = \
            " ".join([str(subst[i]) for i in clause])
        clause_counter += 1

    # Alternative algorithm that uses less memory:
    #    1. record positions of lines.
    #    2. for each (ordered) line in output, seek input, parse, substitute, write.
    for clause in clause_buffer:
        print(clause, file=outputfile)


def substitution(n, variable_permutation=None, polarity_flip=None):
    if variable_permutation is None:
        variable_permutation = list(range(1, n + 1))
        random.shuffle(variable_permutation)
    else:
        assert len(variable_permutation) == n

    vars = [0] + variable_permutation

    if polarity_flip is None:
        polarity_flip = [random.choice([-1, 1]) for x in range(n)]
    else:
        assert len(polarity_flip) == n

    flip = [0] + polarity_flip

    subst = [None] * (2 * n + 1)
    for i, p in enumerate(vars):
        subst[p] = i * flip[p]
    for i in range(1, n + 1):
        subst[-i] = -subst[i]

    return subst
