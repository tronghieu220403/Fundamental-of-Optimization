from random import *

def r(x,y=0):
    return randint(y,x)

from ortools.sat.python import cp_model

import time

BeginTime = time.time()
            
def solve(nStu, nProf, nCouncil):
    
    model = cp_model.CpModel()

    Guide = [0 for _ in range(nStu)]
    for i in range(len(Guide)):
        Guide[i] = r(nProf-1)

    minStu = r(nStu//nCouncil- (r(nStu//nCouncil-2,1))//2,2)
    maxStu = minStu + r(max(2,nStu-nCouncil*minStu), 2)
    
    minProf = r(nProf//nCouncil- (r(nProf//nCouncil-2,1)//2),2)
    maxProf = minProf + r(max(2,nProf-nCouncil*minProf),2)

    #set up cs: council + student
    cs = [[0 for _ in range(nStu)] for __ in range(nCouncil)]

    for b in range(nCouncil):
        for i in range(nStu):
            cs[b][i] = model.NewBoolVar(f'cs_{b}_{i}')

    def cs_once():
        #Once 
        for i in range(nStu):
            model.Add( sum(cs[b][i] for b in range(nCouncil)) == 1)
        return
    cs_once()

    def cs_limit():
        #Number of project in a council >= minStu and <= maxStu
        for b in range(nCouncil):
            model.Add( sum(cs[b][i] for i in range(nStu)) >= minStu)
            
        for b in range(nCouncil):
            model.Add( sum(cs[b][i] for i in range(nStu)) <= maxStu)
        
        return
    cs_limit()

    #set up ct: council + teacher
    ct = [[0 for _ in range(nProf)] for __ in range(nCouncil)]
    for b in range(nCouncil):
        for t in range(nProf):
            ct[b][t] = model.NewBoolVar(f'ct_{b}_{t}')

    def ct_once():
        #Once
        for t in range(nProf):
            model.Add(sum(ct[b][t] for b in range(nCouncil)) == 1)
        return
    ct_once()

    def ct_limit():
        #Number of teacher in a council >= minProf and <= maxProf:
        for b in range(nCouncil):
            model.Add(sum(ct[b][t] for t in range(nProf)) >= minProf)
            model.Add(sum(ct[b][t] for t in range(nProf)) <= maxProf)
        return
    ct_limit()

    #set up ct: student + teacher
    st = [[0 for _ in range(nProf)] for __ in range(nStu)]
    for i in range(nStu):
        for t in range(nProf):
            st[i][t] = model.NewBoolVar(f'st_{i}_{t}')

    def st_set_up():

        for i in range(len(Guide)):
            model.Add(st[i][Guide[i]] == 0)

        return
    st_set_up()


    def st_limit():
        #Number of teacher that a student can meet in his council >= minProf and <= maxProf:
        for i in range(nStu):
            model.Add(sum(st[i][t] for t in range(nProf)) >= minProf)
            model.Add(sum(st[i][t] for t in range(nProf)) <= maxProf)
        #Number of student that a teacher can meet in his council >= minProf and <= maxProf:
        for t in range(nProf):
            model.Add(sum(st[i][t] for i in range(nStu)) >= minStu)
            model.Add(sum(st[i][t] for i in range(nStu)) <= maxStu)

        return
    st_limit()


    #set up ss: student + student
    ss = [[0 for _ in range(nStu)] for __ in range(nStu)]
    for i in range(nStu):
        for j in range(nStu):
            ss[i][j] = model.NewBoolVar(f'ss_{i}_{j}')

    def ss_set_up():
        for i in range(nStu):
            model.Add(ss[i][i] == 0)
        return
    ss_set_up()

    def ss_symmetric():
        for i in range(nStu):
            for j in range(i+1,nStu):
                model.Add(ss[i][j]==ss[j][i])
        return
    ss_symmetric()

    def ss_limit():
        for i in range(nStu):
            model.Add(sum(ss[i][j] for j in range(nStu)) >= minStu-1)
            model.Add(sum(ss[i][j] for j in range(nStu)) <= maxStu-1)
        return
    ss_limit()

    def link_cs_ss():
        for b in range(nCouncil):
            for i in range(nStu):
                for j in range(i+1,nStu):
                    model.Add(cs[b][i] + cs[b][j] <= ss[i][j] +1)
        return
    link_cs_ss()

    def link_cs_ct_st():
        for b in range(nCouncil):
            for i in range(nStu):
                for t in range(nProf):
                    model.Add(cs[b][i] + ct[b][t] <= st[i][t] + 1)
        return
    link_cs_ct_st()

    BeginTime = time.time()

    solver = cp_model.CpSolver()
    solver.parameters.enumerate_all_solutions = False

    status = solver.Solve(model)
    if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        return 0
    
    table = [[0 for __ in range(nStu)] for _ in range(nStu)]
    
    l = []
    
    for i in range(nStu):
        for j in range(nStu):
            if solver.Value(ss[i][j]) > 0:
                table[i][j] = 1
            elif i!=j:
                l.append((i,j))
        
    giveaway = nStu*nStu//7
    for i in range(giveaway):
        if len(l)==0:
            break
        index = r(len(l)-1)
        gg = l[index]
        table[l[index][0]][l[index][1]] = 1
        table[l[index][1]][l[index][0]] = 1
        l.remove((gg[0],gg[1]))
        l.remove((gg[1],gg[0]))
    
    l = []
    
    
    table1 = [[0 for __ in range(nStu)] for _ in range(nProf)]
    
    l = []
    
    for i in range(nStu):
        for t in range(nProf):
            if solver.Value(st[i][t]) > 0:
                table1[t][i] = 1
            elif j!=Guide[i]:
                l.append((t,i))
        
    giveaway = nStu*nProf//7 * 2
    for i in range(giveaway):
        if len(l)==0:
            break
        index = r(len(l)-1)
        table1[l[index][0]][l[index][1]] = 1
        l.remove((l[index][0],l[index][1]))
    
    fout = open("2.out","w")
    def w(x="", end = '\n'):
        fout.write(format(x))
        fout.write(end)
        return
    
    w(str(nStu) + " " + str(nProf) + " " + str(nCouncil))
    minMatchPrj = r(100)
    minMatchPrf = r(100)
    w(str(minStu) + " " + str(maxStu) + " " + str(minProf) + " " + str(maxProf) + " " + str(minMatchPrj) + " " + str(minMatchPrf))
    
    for i in range(nStu):
        for j in range(nStu):
            if table[i][j] > 0:
                w(minMatchPrj+r(minMatchPrj),end = " ")
            else:
                w(minMatchPrj-r(minMatchPrj), end = " ")
        w()
    w()
    for t in range(nProf):
        for i in range(nStu):
            if table1[t][i] == 0:
                w(minMatchPrf-r(minMatchPrf),end = " ")
            else:
                w(minMatchPrf+r(minMatchPrf),end = " ")
        w()
    w()
    for i in range(nStu):
        w(Guide[i]+1,end = " ")
    w()
    return 1

import os

while True:
    n = 80  
    if solve(n,n,r(int(n**0.5)+3,5)) == 0:
        print("No")
        continue
    else:
        print("Yes")
        os.system("python Heuristic_CP_SAT_Solver.py")
        exit()
