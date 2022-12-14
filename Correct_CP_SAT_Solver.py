from ortools.sat.python import cp_model

import time


fileIN = "2.out"

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

model = cp_model.CpModel()

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
    for i in range(nStu):
        for t in range(nProf):
            if PrfData[t][i] < minMachProf:
                model.Add(st[i][t] == 0)

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
        for j in range(nStu):
            if PrjData[i][j] < minMatchStu:
                model.Add(ss[i][j] == 0)
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


#set up cst: council + student + teacher
cst =[[ [ [] for __ in range(nProf)] for ___ in range(nStu) ] for _ in range(nCouncil)]
for b in range(nCouncil):
    for i in range(nStu):
        for t in range(nProf):
            cst[b][i][t] = model.NewBoolVar(f'cst_{b}_{i}_{t}')

for b in range(nCouncil):
    for i in range(nStu):
        for t in range(nProf):
            model.Add(cst[b][i][t] *3 <= cs[b][i] + ct[b][t] + st[i][t])


def cst_exact():
    #Teacher:
    for t in range(nProf):
        model.Add( sum( sum(cst[b][i][t] for i in range(nStu)) for b in range(nCouncil) ) 
                == sum(st[i][t] for i in range(nStu))
        )
    #Student:
    for i in range(nStu):
        model.Add( sum( sum(cst[b][i][t] for t in range(nProf)) for b in range(nCouncil) ) 
                == sum(st[i][t] for t in range(nProf)))
    return

cst_exact()

#set up css: council + student + student
css =[[ [ [] for __ in range(nStu)] for ___ in range(nStu) ] for _ in range(nCouncil)]
for b in range(nCouncil):
    for i in range(nStu):
        for j in range(nStu):
            css[b][i][j] = model.NewBoolVar(f'css_{b}_{i}_{j}')

for b in range(nCouncil):
    for i in range(nStu):
        for j in range(nStu):
            model.Add(css[b][i][j] *3 <= cs[b][i] + cs[b][j] + ss[i][j])

def css_exact():
    # Each council has exact vertexs:
    for i in range(nStu):
        model.Add(sum( sum(css[b][i][j] for j in range(nStu)) for b in range(nCouncil))
        == sum(ss[i][j] for j in range(nStu)))

    return

css_exact()

# Maximize total value of packed items.
objective = []
for b in range(nCouncil):
    for i in range(nStu):
        for j in range(nStu):
            objective.append(cp_model.LinearExpr.Term(css[b][i][j], PrjData[i][j]))
        for t in range(nProf):
            objective.append(cp_model.LinearExpr.Term(cst[b][i][t], PrfData[t][i]))

model.Maximize(cp_model.LinearExpr.Sum(objective))

BeginTime = time.time()

solver = cp_model.CpSolver()
solver.parameters.enumerate_all_solutions = False

status = solver.Solve(model)
if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
    print("No solution.")
    exit()

EndTime = time.time()

ans = int(solver.ObjectiveValue()+0.2)

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
    w()
    w("Teacher: ")
    for t in range(nProf):
        if int(solver.Value(ct[b][t]))>0:
            table[b][1].append(t)
            w(str(t),end = " ")
    w()
    w()

w()
print(f"Answer is: {ans}")
w(f"Answer is: {ans}")
w(f"Solve in {(EndTime-BeginTime)}s")
print(f"Solve in {(EndTime-BeginTime)}s")
print("Answer in "+ fileOut)
