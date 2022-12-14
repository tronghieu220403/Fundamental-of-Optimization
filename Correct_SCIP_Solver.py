from ortools.linear_solver import pywraplp

import time


fileIN = "data.txt"

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

PrfData = [[] for i in range(nProf) ]

for i in range(nProf):
    PrfData[i] = r()

Guide = r()
for i in range(len(Guide)):
    Guide[i] -= 1


BeginTime = time.time()

for i in range(nStu):
    PrjData[i][i]= 0
            
print("LET'S START",flush=True)

solver = pywraplp.Solver.CreateSolver('SCIP')
if solver is None:
    print('SCIP solver unavailable.')
    exit()

#set up cs: council + student
cs = [[0 for _ in range(nStu)] for __ in range(nCouncil)]

for b in range(nCouncil):
    for i in range(nStu):
        cs[b][i] = solver.BoolVar(f'cs_{b}_{i}')

def cs_once():
    #Once
    for i in range(nStu):
        solver.Add( sum(cs[b][i] for b in range(nCouncil)) == 1)
    return
cs_once()

def cs_limit():
    #Number of project in a council >= minStu and <= maxStu
    for b in range(nCouncil):
        solver.Add( sum(cs[b][i] for i in range(nStu)) >= minStu)
        
    for b in range(nCouncil):
        solver.Add( sum(cs[b][i] for i in range(nStu)) <= maxStu)
    
    return
cs_limit()

#set up ct: council + teacher
ct = [[0 for _ in range(nProf)] for __ in range(nCouncil)]
for b in range(nCouncil):
    for t in range(nProf):
        ct[b][t] = solver.BoolVar(f'ct_{b}_{t}')

def ct_once():
    #Once
    for t in range(nProf):
        solver.Add(sum(ct[b][t] for b in range(nCouncil)) == 1)
    return
ct_once()

def ct_limit():
    #Number of teacher in a council >= minProf and <= maxProf:
    for b in range(nCouncil):
        solver.Add(sum(ct[b][t] for t in range(nProf)) >= minProf)
        solver.Add(sum(ct[b][t] for t in range(nProf)) <= maxProf)
    return
ct_limit()

#set up ct: student + teacher
st = [[0 for _ in range(nProf)] for __ in range(nStu)]
for i in range(nStu):
    for t in range(nProf):
        st[i][t] = solver.BoolVar(f'st_{i}_{t}')

def st_set_up():
    for i in range(nStu):
        for t in range(nProf):
            if PrfData[t][i] < minMachProf:
                solver.Add(st[i][t] == 0)

    for i in range(len(Guide)):
        solver.Add(st[i][Guide[i]] == 0)

    return
st_set_up()


def st_limit():
    #Number of teacher that a student can meet in his council >= minProf and <= maxProf:
    for i in range(nStu):
        solver.Add(sum(st[i][t] for t in range(nProf)) >= minProf)
        solver.Add(sum(st[i][t] for t in range(nProf)) <= maxProf)
    #Number of student that a teacher can meet in his council >= minProf and <= maxProf:
    for t in range(nProf):
        solver.Add(sum(st[i][t] for i in range(nStu)) >= minStu)
        solver.Add(sum(st[i][t] for i in range(nStu)) <= maxStu)

    return
st_limit()


#set up ss: student + student
ss = [[0 for _ in range(nStu)] for __ in range(nStu)]
for i in range(nStu):
    for j in range(nStu):
        ss[i][j] = solver.BoolVar(f'ss_{i}_{j}')

def ss_set_up():
    for i in range(nStu):
        solver.Add(ss[i][i] == 0)
        for j in range(nStu):
            if PrjData[i][j] < minMatchStu:
                solver.Add(ss[i][j] == 0)
    return
ss_set_up()

def ss_symmetric():
    for i in range(nStu):
        for j in range(i+1,nStu):
            solver.Add(ss[i][j]==ss[j][i])
    return
ss_symmetric()

def ss_limit():
    for i in range(nStu):
        solver.Add(sum(ss[i][j] for j in range(nStu)) >= minStu-1)
        solver.Add(sum(ss[i][j] for j in range(nStu)) <= maxStu-1)
    return
ss_limit()

def link_cs_ss():
    for b in range(nCouncil):
        for i in range(nStu):
            for j in range(i+1,nStu):
                solver.Add(cs[b][i] + cs[b][j] <= ss[i][j] +1)
    return
link_cs_ss()

def link_cs_ct_st():
    for b in range(nCouncil):
        for i in range(nStu):
            for t in range(nProf):
                solver.Add(cs[b][i] + ct[b][t] <= st[i][t] + 1)
    return
link_cs_ct_st()

# Maximize total value of packed items.
objective = solver.Objective()
for i in range(nStu):
    for j in range(nStu):
        objective.SetCoefficient(ss[i][j], PrjData[i][j])
    for t in range(nProf):
        objective.SetCoefficient(st[i][t], PrfData[t][i])

objective.SetMaximization()

BeginTime = time.time()

status = solver.Solve()

if status not in [pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE]:
    print("No solution.")
    exit()

EndTime = time.time()

ans = int(objective.Value()+0.2)

fileOut = "1.out"
fout = open(fileOut,"w")
def w(x="",end='\n'):
    fout.write(format(x))
    fout.write(end)

for b in range(nCouncil):
    w("Council "+ str(b+1))
    w("Project: ")
    for i in range(nStu):
        if int(cs[b][i].solution_value())>0:
            w(str(i),end = " ")
    w("Teacher: ")
    for t in range(nProf):
        if int(ct[b][t].solution_value())>0:
            w(str(t),end = " ")
    w()

w()
print(f"Answer is: {ans}")
w(f"Answer is: {ans}")
w(f"Solve in {(EndTime-BeginTime)}s")
print(f"Solve in {(EndTime-BeginTime)}s")
print("Answer in "+ fileOut)
