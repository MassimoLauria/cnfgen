#!/usr/bin/env python
# -*- coding:utf-8 -*-

from cnfformula.cnf import CNF

import cnfformula.cmdline
import cnfformula.families

from itertools import product

import networkx
from cnfformula.families.tseitin import TseitinFormula
from itertools import combinations

@cnfformula.families.register_cnf_generator
def PitfallFormula(v,d,ny,nz,k):

    def xname(j,x):
        return "{}_{}".format(x,j)

    phi = CNF()
    graph = networkx.random_regular_graph(d,v)
    charge = [1]+[0]*(v-1)
    ts = TseitinFormula(graph,charge)

    X_ = list(ts.variables())
    nx = len(X_)

    X = [0]*k
    P = [0]*k
    Y = [0]*k
    Z = [0]*k
    A = [0]*k
    for j in range(k):
        X[j] = [xname(j,x) for x in X_]
        P[j] = ["p_{}_{}".format(j,i) for i in range(nx+nz)]
        Y[j] = ["y_{}_{}".format(j,i) for i in range(ny)]
        Z[j] = ["z_{}_{}".format(j,i) for i in range(nz)]
        A[j] = ["a_{}_{}".format(j,i) for i in range(3)]

    for YY in Y:
        for y in YY:
            phi.add_variable(y)

    for XX in X:
        for x in XX:
            phi.add_variable(x)

    # Ts_j
    for j in range(k):
        append = [(True,z) for z in Z[j]]
        for C in ts:
            CC=[(p,xname(j,x)) for (p,x) in C]
            phi.add_clause(CC + append)

    # Psi
    def pitfall(y1,y2,PP):
        CY = [(True,y1),(True,y2)]
        for p in PP:
            phi.add_clause(CY+[(False,p)])

    for j in range(k):
        for (y1,y2) in combinations(Y[j],2):
            pitfall(y1,y2,P[j])

    # Pi
    def pipe(y,PP,XX,ZZ):
        S = XX+ZZ
        CY = [(True,y)]
        C = []
        for (s,PPP) in zip(S,combinations(PP,len(PP)-1)):
            CP = [(True,p) for p in PPP]
            CS = C
            if len(CS)+1==len(S):
                # C_{m+n} does not contain z_1
                del CS[nx]
            phi.add_clause(CY+CP+CS+[(False,s)])
            C.append((True,s))

    for j in range(k):
        for y in Y[j]:
            pipe(y,P[j],X[j],Z[j])

    # Delta
    def tail(y,z,AA):
        phi.add_clause([(False,AA[0]),(True,AA[2]),(False,z)])
        phi.add_clause([(False,AA[1]),(False,AA[2]),(False,z)])
        phi.add_clause([(True,AA[0]),(False,z),(False,y)])
        phi.add_clause([(True,AA[1]),(False,z),(False,y)])

    for j in range(k):
        for (y,z) in product(Y[j],Z[j]):
            tail(y,z,A[j])

    # Gamma
    split_gamma = 2
    for i in range(0,ny,split_gamma):
        phi.add_clause([(False,Y[j][i+ii]) for j in range(k) for ii in range(split_gamma)])

    return phi

@cnfformula.cmdline.register_cnfgen_subcommand
class PitfallCmdHelper(object):
    name='pitfall'
    description='Pitfall formula'

    @staticmethod
    def setup_command_line(parser):
        parser.add_argument('v',type=int)
        parser.add_argument('d',type=int)
        parser.add_argument('ny',type=int)
        parser.add_argument('nz',type=int)
        parser.add_argument('k',type=int)

    @staticmethod
    def build_cnf(args):
        return PitfallFormula(args.v, args.d, args.ny, args.nz, args.k)
