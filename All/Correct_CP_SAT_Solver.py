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

PrfData = [[] for i in range(nProf) ]

for i in range(nProf):
    PrfData[i] = r()

Guide = r()
for i in range(len(Guide)):
    Guide[i] -= 1

BeginTime = time.time()

for i in range(nStu):
    PrjData[i][i]= 0

BeginTime = time.time()

print("LET'S START",flush=True)

table = [[[] for __ in range(2)] for _ in range(nCouncil)]

ans = 0

def solve(e, f, getMax = 0):
    
    minMatchStu = e
    minMachProf = f
    
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

    solver = cp_model.CpSolver()
    
    if getMax == 1:
        class SolutionPrinter(cp_model.CpSolverSolutionCallback):
            """Print intermediate solutions."""

            def __init__(self):
                cp_model.CpSolverSolutionCallback.__init__(self)

            # calculate solution here
            def on_solution_callback(self):
                _cs = [[0 for _ in range(nStu)] for __ in range(nCouncil)]
                _ct = [[0 for _ in range(nProf)] for __ in range(nCouncil)]
                _table = [[[] for __ in range(2)] for _ in range(nCouncil)]
                _ans = 0
                for b in range(nCouncil):
                    for i in range(nStu):
                        if self.BooleanValue(cs[b][i]) > 0:
                            _table[b][0].append(i)
                    for t in range(nProf):
                        if self.BooleanValue(ct[b][t]) > 0:
                            _table[b][1].append(t)
                
                for b in range(nCouncil):
                    for i in _table[b][0]:
                        for j in _table[b][0]:
                            if i!=j:
                                _ans += PrjData[i][j]    
                        for t in _table[b][1]:
                            _ans += PrfData[t][i]

                global table
                global ans
                if (ans<_ans):
                    table = _table
                    ans = _ans
        
                return

        solver.parameters.enumerate_all_solutions = True
        solver.parameters.max_time_in_seconds = 60.0
        callback = SolutionPrinter()
        status = solver.Solve(model,callback)
        if status not in [cp_model.OPTIMAL]:
            return 0
    else:
        solver.parameters.enumerate_all_solutions = False
        status = solver.Solve(model)
        if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            return 0

    return 1


eMax = 0
fMax = 0

eleft = 0
fleft = 0

eArr = list(sorted(list(set(list(chain.from_iterable(PrjData))))))
fArr = list(sorted(list(set(list(chain.from_iterable(PrfData))))))

fright = len(fArr)-1
eright = len(eArr)-1
mid = 0

emax = -1

RunTime = 0

while(eleft<=eright):
    mid = (eleft+eright)//2
    if solve(eArr[mid],fArr[0])==1:
        emax = max(emax,mid)
        eleft = mid + 1
    else:
        eright = mid - 1

if emax == -1:
    print("No solution")
    exit()

fmax = -1

while(fleft<=fright):
    mid = (fleft+fright)//2
    if solve(eArr[emax], fArr[mid])==1:
        fmax = max(fmax,mid)
        fleft = mid + 1
    else:
        fright = mid - 1

if fmax == -1:
    print("No solution")
    exit()

if (solve(eArr[emax],fArr[fmax],1) == 0):
    print("No solution")
    exit()
    
EndTime = time.time()

fileOut = "CorrectAns.out"
fout = open(fileOut,"w")
def w(x="",end='\n'):
    fout.write(format(x))
    fout.write(end)

w(f"Maximum value of e and f are:\n{eArr[emax]} {fArr[fmax]}\n")
print(f"Maximum value of and f are {eArr[emax]} and {fArr[fmax]}")

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