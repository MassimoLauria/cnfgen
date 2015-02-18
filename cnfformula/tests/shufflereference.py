from __future__ import print_function
import random

def stableshuffle(inputfile,
                  outputfile,
                  variable_permutation=None,
                  clause_permutation=None,
                  polarity_flip=None):

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
            subst = substitution(n, variable_permutation, polarity_flip)
            m = int(mstr)

            # Clause permutation
            if clause_permutation==None:
                clause_permutation=range(m)
                random.shuffle(clause_permutation)
            
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

        clause_buffer[clause_permutation[clause_counter]] = \
            " ".join([str(subst[i]) for i in clause])
        clause_counter += 1

    # Alternative algorithm that uses less memory:
    #    1. record positions of lines.
    #    2. for each (ordered) line in output, seek input, parse, substitute, write.
    for clause in clause_buffer :
        print(clause,file=outputfile)


def substitution(n, variable_permutation = None,
                 polarity_flip = None) :
    if variable_permutation is None :
        variable_permutation = range(1,n+1)
        random.shuffle(variable_permutation)
    else:
        assert len(variable_permutation)==n

    vars = [0] + variable_permutation

    if polarity_flip is None :
        polarity_flip = [random.choice([-1,1]) for x in xrange(n)]
    else:
        assert len(polarity_flip)==n

    flip = [0] + polarity_flip

    subst=[None]*(2*n+1)
    for i,p in enumerate(vars):
        subst[p]=i*flip[p]
    for i in xrange(1,n+1):
        subst[-i]= -subst[i]

    return subst
