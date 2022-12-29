from ortools.sat.python import cp_model

import time

fileIN = "1.inp"
finp = open(fileIN,"r")

nStu, nProf, nCouncil = map(int, finp.readline().split())
minStu, maxStu, minProf, maxProf, minMatchStu, minMachProf = map(int, finp.readline().split())

def r():
    while True:
        xx = finp.readline()
        if len(xx) == 1:
            continue
        return list(map(int, xx.split()))
        
PrjData = [[] for i in range(nStu) ]
for i in range(nStu):
    PrjData[i] = r()
    PrjData[i][i]= 0

PrfData = [[] for i in range(nProf) ]
for i in range(nProf):
    PrfData[i] = r()

Guide = r()
for i in range(len(Guide)):
    Guide[i] -= 1

BeginTime = time.time()
            
print("LET'S START",flush=True)

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
    #Number of project in a council >= minStu and <= maxStu
    for b in range(nCouncil):
        model.Add(sum(cs[b][i] for i in range(nStu)) >= minStu)
        
    for b in range(nCouncil):
        model.Add(sum(cs[b][i] for i in range(nStu)) <= maxStu)
    
    return
cs_limit()

def ct_limit():
    #Number of teacher in a council >= minProf and <= maxProf:
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


BeginTime = time.time()

solver = cp_model.CpSolver()
solver.parameters.enumerate_all_solutions = False

status = solver.Solve(model)
if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
    print("No solution.")
    exit()

print("FINISH!",flush=True)
    
EndTime = time.time()

ans = 0

fileOut = "1.out"
fout = open(fileOut,"w")
def w(x="",end='\n'):
    fout.write(format(x))
    fout.write(end)

table = [[[] for __ in range(2)] for _ in range(nCouncil)]

for b in range(nCouncil):
    w("Council "+ str(b+1))
    w("Project: ")
    for i in range(nStu):
        if int(solver.Value(cs[b][i]))>0:
            table[b][0].append(i)
            w(str(i),end = " ")
    #w(table[b][0])
    w()
    w("Teacher: ")
    for t in range(nProf):
        if int(solver.Value(ct[b][t]))>0:
            table[b][1].append(t)
            w(str(t),end = " ")
    #w(table[b][1])
    w()
    w()

for b in range(nCouncil):
    for i in table[b][0]:
        for j in table[b][0]:
            ans += PrjData[i][j] if i!=j else 0
        for t in table[b][1]:
            ans += PrfData[t][i]

w()
print(f"Answer is: {ans}")
w(f"Answer is: {ans}")
w(f"Solve in {(EndTime-BeginTime)}s")
print(f"Solve in {(EndTime-BeginTime)}s")
print("Answer in "+ fileOut)
