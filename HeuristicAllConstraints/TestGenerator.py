from random import *
from Project26Heuristic import CP
def r(x,y=0):
    return randint(y,x)

from ortools.sat.python import cp_model

import time

BeginTime = time.time()
table = []
table1 = []

ss1 = []
st1 = []
def solve(nStu, nProf, nCouncil):
    
    model = cp_model.CpModel()

    Guide = [0 for _ in range(nStu)]
    for i in range(len(Guide)):
        Guide[i] = r(nProf-1)

    minStu = r(nStu//nCouncil- (r(max(nStu//nCouncil-2,1),1))//2,2)
    maxStu = minStu + r(max(2,nStu-nCouncil*minStu), 2)
    
    minProf = r(nProf//nCouncil- (r(max(nProf//nCouncil-2,1),1)//2),2)
    maxProf = minProf + r(max(2,nProf-nCouncil*minProf),2)

    #set up cs: council + student
    cs = [[0 for _ in range(nStu)] for __ in range(nCouncil)]
    for b in range(nCouncil):
        for i in range(nStu):
            cs[b][i] = model.NewBoolVar(f'cs_{b}_{i}')

    #set up ct: council + teacher
    ct = [[0 for _ in range(nProf)] for __ in range(nCouncil)]
    for b in range(nCouncil):
        for t in range(nProf):
            ct[b][t] = model.NewBoolVar(f'ct_{b}_{t}')

    def cs_once():
        #Once
        for i in range(nStu):
            model.AddExactlyOne(cs[b][i] for b in range(nCouncil))
        return
    cs_once()
    
    def ct_once():
        #Once
        for t in range(nProf):
            model.AddExactlyOne(ct[b][t] for b in range(nCouncil))
        return
    ct_once()
    
    def cs_limit():
        #Number of project in a council >= minStu and <= maxStu
        for b in range(nCouncil):
            model.Add( sum(cs[b][i] for i in range(nStu)) >= minStu)
            
        for b in range(nCouncil):
            model.Add( sum(cs[b][i] for i in range(nStu)) <= maxStu)
        
        return
    cs_limit()

    def ct_limit():
        #Number of teacher in a council >= minProf and <= maxProf:
        for b in range(nCouncil):
            model.Add(sum(ct[b][t] for t in range(nProf)) >= minProf)
            model.Add(sum(ct[b][t] for t in range(nProf)) <= maxProf)
        return
    ct_limit()
    
    BeginTime = time.time()

    solver = cp_model.CpSolver()
    solver.parameters.enumerate_all_solutions = False
    solver.parameters.max_time_in_seconds = 10.0

    status = solver.Solve(model)
    if status in [cp_model.UNKNOWN]:
        return 0

    if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        return 0
    
    table = [[0 for __ in range(nStu)] for _ in range(nStu)]
    
    l = []
    ss = [[0 for _ in range(nStu)] for __ in range(nStu)]
    st = [[0 for _ in range(nProf)] for __ in range(nStu)]

    for b in range(nCouncil):
        for i in range(nStu):
            for j in range(i+1,nStu):
                if solver.BooleanValue(cs[b][i]) > 0 and solver.BooleanValue(cs[b][j]) > 0:
                    ss[i][j] = 1
                    ss[j][i] = 1
            for t in range(nProf):
                if solver.BooleanValue(cs[b][i]) > 0 and solver.BooleanValue(ct[b][t]) > 0:
                    st[i][t] = 1

    for i in range(nStu):
        for j in range(i+1,nStu):
            if (ss[i][j]) > 0:
                table[i][j] = 1
                table[j][i] = 1
            elif i!=j:
                l.append((i,j))

    giveaway = nStu*nStu//4
    sz = len(l)
    for i in range(giveaway):
        if sz==0:
            break
        index = r(sz-1)
        table[l[index][0]][l[index][1]] = 1
        table[l[index][1]][l[index][0]] = 1
        l[index],l[sz-1] = l[sz-1],l[index]
        sz = sz - 1
        
        
    table1 = [[0 for __ in range(nStu)] for _ in range(nProf)]
    
    l = []

    for i in range(nStu):
        for t in range(nProf):
            if (st[i][t]) > 0:
                table1[t][i] = 1
            elif j!=Guide[i]:
                l.append((t,i))
    sz = len(l)
    giveaway = nStu*nProf//4 * 2
    for i in range(giveaway):
        if sz==0:
            break
        index = r(sz-1)
        table1[l[index][0]][l[index][1]] = 1
        l[index],l[sz-1] = l[sz-1],l[index]
        sz = sz-1
    
    fout = open("1.inp","w")
    def w(x="", end = '\n'):
        fout.write(format(x))
        fout.write(end)
        return

    w(str(nStu) + " " + str(nProf) + " " + str(nCouncil))
    minMatchPrj = r(150,50)
    minMatchPrf = r(150,50)
    w(str(minStu) + " " + str(maxStu) + " " + str(minProf) + " " + str(maxProf) + " " + str(minMatchPrj) + " " + str(minMatchPrf))
    
    for i in range(nStu):
        for j in range(nStu):
            if table[i][j] > 0:
                w(minMatchPrj+r(minMatchPrj)+10,end = " ")
            else:
                w(minMatchPrj-r(minMatchPrj)+10, end = " ")
        w()
    w()
    for t in range(nProf):
        for i in range(nStu):
            if table1[t][i] == 0:
                w(minMatchPrf-r(minMatchPrf//2)+10,end = " ")
            else:
                w(minMatchPrf+r(minMatchPrf)+10,end = " ")
        w()
    w()
    for i in range(nStu):
        w(Guide[i]+1,end = " ")
    w()
    fout.close()

    return 1

import os

finp = open("2.out","r")

def read():
    global finp
    while True:
        xx = finp.readline()
        if "optimal" in xx:
            return -1
        if len(xx) == 1 or "C" in xx or ":" in xx:
            continue
        return list(map(int, xx.split()))

def check():
    print("Checking...")
    x = CP("1.inp")
    StuData, PrfData = x.ReadInput()
    l = read()
    if l == -1:
        return
    #print(l)
    e, f = l[0],l[1]
    nCouncil = x.GetValue("nCouncil")
    for b in range(nCouncil):
        Stu = read()
        Prf = read()
        for i in Stu:
            for j in Stu:
                if i!=j:
                    if StuData[i][j] < e:
                        raise ValueError(f'Wrong in StuData: {i} {j}: {StuData[i][j]} < {e}')
            for t in Prf:
                if PrfData[t][i] < f:
                    raise ValueError(f'Wrong in PrfData: {t} {i}: {PrfData[t][i]} < {f}')
    finp.close()
    print("No error found.")
    return

def GenerateAndCheck(NumTest,n,m):
    for _ in range(NumTest):
        print('\nTest case ' + str(_))
        print("Finding a case...")
        while True:
            n = 500
            nCouncil = r(int(n**0.5)+3,5)
            if solve(n,n,nCouncil) == 0:
                print("Can not find a case. Trying again...")
                continue
            else:
                print("Found a case.")
                os.system("python MaximizeEF.py")
                finp = open("2.out","r")
                check()
                finp.close()
                break

def CheckOnly():
    os.system("python MaximizeEF.py")
    check()

#Generate input to 1.inp and check the result.
#GenerateAndCheck(1,50,50) #n and m are number of students and number of teachers

CheckOnly() #if you already have an input file "1.inp", you can check your code with that test case by using this.
    
