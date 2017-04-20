from __future__ import print_function
import random

def stableshuffle(inputfile,
                  outputfile,
                  variables_permutation=None,
                  clauses_permutation=None,
                  polarity_flips=None):

    subst= None
    line_counter = 0
    header_buffer=["c Reshuffling of:\nc\n"]
    clause_counter = 0

    for l in inputfile.readlines():

        line_counter+=1

        # add the comment to the header (discard if it is in the middle)
        if l[0]=='c':
            if not subst: header_buffer.append(l)
            continue
    
        # parse spec line
        if l[0]=='p':
            if subst:
                raise ValueError("Syntax error: "+
                                 "line {} contains a second spec line.".format(line_counter))
            _,_,nstr,mstr = l.split()
            n = int(nstr)
            subst = substitution(n, variables_permutation, polarity_flips)
            m = int(mstr)

            # Clause permutation
            if clauses_permutation==None:
                clauses_permutation=range(m)
                random.shuffle(clauses_permutation)
            
            clause_buffer=[None]*m

            # Print header
            for h in header_buffer:
                print(h,end='',file=outputfile)
            
            print(l,end='',file=outputfile)
            
            continue

        # parse literals
        clause = [int(lit) for lit in l.split()]

        # Checks at the end of clause
        if clause[-1] != 0:
            raise ValueError("Syntax error: last clause was incomplete")

        clause_buffer[clauses_permutation[clause_counter]] = \
            " ".join([str(subst[i]) for i in clause])
        clause_counter += 1

    # Alternative algorithm that uses less memory:
    #    1. record positions of lines.
    #    2. for each (ordered) line in output, seek input, parse, substitute, write.
    for clause in clause_buffer :
        print(clause,file=outputfile)


def substitution(n, variables_permutation = None,
                 polarity_flips = None) :
    if variables_permutation is None :
        variables_permutation = range(1,n+1)
        random.shuffle(variables_permutation)
    else:
        assert len(variables_permutation)==n

    vars = [0] + variables_permutation

    if polarity_flips is None :
        polarity_flips = [random.choice([-1,1]) for x in xrange(n)]
    else:
        assert len(polarity_flips)==n

    flip = [0] + polarity_flips

    subst=[None]*(2*n+1)
    for i,p in enumerate(vars):
        subst[p]=i*flip[p]
    for i in xrange(1,n+1):
        subst[-i]= -subst[i]

    return subst
