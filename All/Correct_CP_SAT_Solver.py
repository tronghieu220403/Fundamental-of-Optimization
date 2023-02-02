from ortools.sat.python import cp_model

import time
from itertools import chain

fileIN = "data.inp"

finp = open(fileIN,"r")

nStu, nProf, nCouncil = map(int, finp.readline().split())

minStu, maxStu, minProf, maxProf, minMatchStu, minMachProf = map(int, finp.readline().split())

PrjData = [[] for i in range(nStu) ]

def r():
    while True:
        xx = finp.readline()
        if len(xx) == 1:
            continue
        return list(map(int, xx.split()))
        
for i in range(nStu):
    PrjData[i] = r()

PrfData = [[0 for __ in range(nStu)] for _ in range(nProf) ]

for i in range(nStu):
    xx = r()
    for _t in range(len(xx)):
        PrfData[_t][i] = xx[_t]

Guide = r()
for i in range(len(Guide)):
    Guide[i] -= 1

BeginTime = time.time()

for i in range(nStu):
    PrjData[i][i]= 0

BeginTime = time.time()

table = [[[] for __ in range(2)] for _ in range(nCouncil)]

ans = 0

def solve(getMax = 0):
        
    model = cp_model.CpModel()

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
        #Number of project in a council >= miniStu and <= maxStu
        for b in range(nCouncil):
            model.Add( sum(cs[b][i] for i in range(nStu)) >= minStu)
            model.Add( sum(cs[b][i] for i in range(nStu)) <= maxStu)

        return
    cs_limit()

    def ct_limit():
        #Number of teacher in a council >= miniProf and <= maxProf:
        for b in range(nCouncil):
            model.Add(sum(ct[b][t] for t in range(nProf)) >= minProf)
            model.Add(sum(ct[b][t] for t in range(nProf)) <= maxProf)
        return
    ct_limit()

    def link_cs_cs():
        for b in range(nCouncil):
            for i in range(nStu):
                for j in range(i+1,nStu):
                    if PrjData[i][j] < minMatchStu or PrjData[j][i] < minMatchStu:
                        model.AddAtMostOne([cs[b][i], cs[b][j]])
        return
    link_cs_cs()

    def link_cs_ct():
        for b in range(nCouncil):
            for i in range(nStu):
                for t in range(nProf):
                    if PrfData[t][i] < minMachProf or t == Guide[i]:
                        model.AddAtMostOne([cs[b][i], ct[b][t]])
        return
    link_cs_ct()

    ss = [[0 for _ in range(nStu)] for __ in range(nStu)]
    for i in range(nStu):
        for j in range(nStu):
            ss[i][j] = model.NewBoolVar(f'ss_{i}_{j}')
            model.AddMaxEquality(ss[i][j], [cs[b][i] + cs[b][j]-1 for b in range(nCouncil)])

    #set up ct: council + teacher
    st = [[0 for _ in range(nProf)] for __ in range(nStu)]
    for i in range(nStu):
        for t in range(nProf):
            st[i][t] = model.NewBoolVar(f'st_{i}_{t}')
            model.AddMaxEquality(st[i][t],[cs[b][i]+ct[b][t]-1 for b in range(nCouncil)])

    #maxmatch = sum(PrjData[i][j] for j in range(nStu) for i in range(nStu)) + sum(PrfData[t][i] for i in range(nStu) for t in range(nProf)
    #minAns = model.NewIntVar(0, , 'min_time')
    model.Maximize(sum(ss[i][j]*PrjData[i][j] for j in range(nStu) for i in range(nStu)) + sum(st[i][t]*PrfData[t][i] for i in range(nStu) for t in range(nProf)))

    solver = cp_model.CpSolver()
    
    status = solver.Solve(model)
    
    if status not in [cp_model.OPTIMAL]:
        return 0
    
    for b in range(nCouncil):
        for i in range(nStu):
            if solver.BooleanValue(cs[b][i]) > 0:
                table[b][0].append(i)
        for t in range(nProf):
            if solver.BooleanValue(ct[b][t]) > 0:
                table[b][1].append(t)
    
    return 1

solve()

EndTime = time.time()

fileOut = "CorrectAns.out"
fout = open(fileOut,"w")
def w(x="",end='\n'):
    fout.write(format(x))
    fout.write(end)

ans = 0


for b in range(nCouncil):
    w(f"Council {b+1}:")
    w(f"{len(table[b][0])} project:")
    for i in table[b][0]:
        w(i+1,end = " ")
    w()
    w(f"{len(table[b][1])} teacher:")
    for t in table[b][1]:
        w(t+1,end =" ")
    w('\n')

for b in range(nCouncil):
    for i in table[b][0]:
        for j in table[b][0]:
            if i!=j:
                ans += PrjData[i][j]    
        for t in table[b][1]:
            ans += PrfData[t][i]

w()
print(f"Answer is: {ans}")
w(f"Answer is: {ans}")
w(f"Solve in {(EndTime-BeginTime)}s")
print(f"Solve in {(EndTime-BeginTime)}s")
print("Answer in "+ fileOut)