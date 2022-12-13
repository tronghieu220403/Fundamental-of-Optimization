from ortools.linear_solver import pywraplp

import time

fileIn = "data.txt"
finp = open(fileIn,"r")

fileOut = "1.out"
fout = open(fileOut,"w")
def w(x="",end='\n'):
    fout.write(format(x))
    fout.write(end)

nStu, nProf, nCouncil = map(int, finp.readline().split())

minStu, maxStu, minProf, maxProf, minMatchPrj, minMachPrf = map(int, finp.readline().split())

PrjData = [[] for i in range(nStu) ]

index = [[] for i in range(nStu)]

def r():
    while True:
        xx = finp.readline()
        if len(xx) == 1:
            continue
        return list(map(int, xx.split()))
        
for i in range(nStu):
    while True:
        xx = finp.readline()
        if len(xx) == 1:
            continue
        PrjData[i] = list(map(int, xx.split()))
        break

PrfData = [[] for i in range(nProf) ]

for i in range(nProf):
    while True:
        xx = finp.readline()
        if len(xx) == 1:
            continue
        PrfData[i] = list(map(int, xx.split()))
        break

Guide = []

while True:
    xx = finp.readline()
    if len(xx) == 1:
        continue
    Guide = list(map(int, xx.split()))
    for i in range(len(Guide)):
        Guide[i] -= 1
    break

BeginTime = time.time()

for i in range(nStu):
    PrjData[i][i]= -999999
    for j in range(nStu):
        if PrjData[i][j] < minMatchPrj:
            PrjData[i][j]= -999999
            PrjData[j][i]= -999999
'''
for i in range(nStu):
    for j in range(i+1,nStu):
        if PrjData[i][j] != PrjData[j][i]:
            PrjData[i][j]= -999999
            PrjData[j][i]= -999999 
'''
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


#Once
for i in range(nStu):
    solver.Add( sum(cs[b][i] for b in range(nCouncil)) == 1)

#Number of project in a council >= minStu and <= maxStu
for b in range(nCouncil):
    solver.Add( sum(cs[b][i] for i in range(nStu)) >= minStu)
    
for b in range(nCouncil):
    solver.Add( sum(cs[b][i] for i in range(nStu)) <= maxStu)

#set up ct: council + teacher
ct = [[0 for _ in range(nProf)] for __ in range(nCouncil)]
for b in range(nCouncil):
    for t in range(nProf):
        ct[b][t] = solver.BoolVar(f'ct_{b}_{t}')

#Once
for t in range(nProf):
    solver.Add(sum(ct[b][t] for b in range(nCouncil)) == 1)

#Number of teacher in a council >= minProf and <= maxProf:
for b in range(nCouncil):
    solver.Add(sum(ct[b][t] for t in range(nProf)) >= minProf)
    solver.Add(sum(ct[b][t] for t in range(nProf)) <= maxProf)

#set up ct: student + teacher
st = [[0 for _ in range(nProf)] for __ in range(nStu)]
for i in range(nStu):
    for t in range(nProf):
        st[i][t] = solver.BoolVar(f'st_{i}_{t}')

#Number of teacher that a student can meet in his council >= minProf and <= maxProf:
for i in range(nStu):
    solver.Add(sum(st[i][t] for t in range(nProf)) >= minProf)
    solver.Add(sum(st[i][t] for t in range(nProf)) <= maxProf)

for i in range(nStu):
    for t in range(nProf):
        if PrfData[t][i] < minMachPrf:
            solver.Add(st[i][t] == 0)

for i in range(len(Guide)):
    solver.Add(st[i][Guide[i]] == 0)
    PrfData[Guide[i]][i]  = -999999

#set up ss: student + student
ss = [[0 for _ in range(nStu)] for __ in range(nStu)]
for i in range(nStu):
    for j in range(nStu):
        ss[i][j] = solver.BoolVar(f'ss_{i}_{j}')

for i in range(nStu):
    for j in range(nStu):
        if PrjData[i][j] < minMatchPrj:
            PrjData[i][j] = -999999
            solver.Add(ss[i][j] == 0)

for i in range(nStu):
    for j in range(i+1,nStu):
        solver.Add(ss[i][j]==ss[j][i])

#set up cst: council + student + teacher
cst =[[ [ [] for __ in range(nProf)] for ___ in range(nStu) ] for _ in range(nCouncil)]
for b in range(nCouncil):
    for i in range(nStu):
        for t in range(nProf):
            cst[b][i][t] = solver.BoolVar(f'cst_{b}_{i}_{t}')

for b in range(nCouncil):
    for i in range(nStu):
        for t in range(nProf):
            solver.Add(cst[b][i][t] *3 <= cs[b][i] + ct[b][t] + st[i][t])

'''
for i in range(nStu):
    for t in range(nProf):
        if PrfData[t][i] < minMachPrf:
            for b in range(nCouncil):
                solver.Add(cst[b][i][t] == 0)

for i in range(len(Guide)):
    for b in range(nCouncil):
        w(f"{i}_{Guide[i]}")
        solver.Add(cst[b][i][Guide[i]] == 0)
'''

#Once
def cst_once():
    #part 1: a teacher CAN NOT assign in MORE THAN ONE council
    for t in range(nProf):
        for j in range(nStu):
            for b in range(nCouncil):
                for f in range(nCouncil):
                    if b!=f:
                        for l in range(nStu):
                            solver.Add(cst[b][j][t] + cst[f][l][t] <= 1)
    #part 2: a teacher must be placed in AT LEAST ONE council
    for t in range(nProf):
        solver.Add( sum( sum(cst[b][i][t] for i in range(nStu)) for b in range(nCouncil) ) >= 1)
    return

cst_once()

def cst_max_graph():
    for i in range(nStu):
        solver.Add(sum( sum(cst[b][i][t] for b in range(nCouncil)) for t in range(nProf) ) 
        == sum(st[i][t] for t in range(nProf)) )
    for t in range(nProf):
        solver.Add(sum (sum(cst[b][i][t] for b in range(nCouncil)) for i in range(nStu))
        == sum(st[i][t] for i in range(nStu)))

cst_max_graph()

def cst_all_link():
    for b in range(nCouncil):
        for i in range(nStu):
            for t in range(nProf):
                for i1 in range(nStu):
                    if PrfData[t][i1] < minMachPrf:
                        for t1 in range(nProf):
                            solver.Add(cst[b][i][t] + cst[b][i1][t1] <= 1)            
    pass

cst_all_link()

#set up css: council + student + student
css =[[ [ [] for __ in range(nStu)] for ___ in range(nStu) ] for _ in range(nCouncil)]
for b in range(nCouncil):
    for i in range(nStu):
        for j in range(nStu):
            css[b][i][j] = solver.BoolVar(f'css_{b}_{i}_{j}')

for b in range(nCouncil):
    for i in range(nStu):
        for j in range(nStu):
            if i!=j:
                solver.Add(css[b][i][j] *3 <= cs[b][i] + cs[b][j] + ss[i][j])


# Each project is assigned to at most one council.
def css_once(): #only one at one council
    #part 1: a student CAN NOT assign his edges in MORE THAN ONE council
    for i in range(nStu):
        for j in range(nStu):
            for b in range(nCouncil):
                for f in range(nCouncil):
                    if b!=f:
                        for l in range(nStu):
                            solver.Add(css[b][i][j] + css[f][i][l] <= 1)
    #part 2: a student must be placed in AT LEAST ONE council
    for i in range(nStu):
        solver.Add( sum( sum(css[b][i][j] for j in range(nStu)) for b in range(nCouncil) ) >= 1)
    return
    
#done

# css[b,i,j] must be symmetric, i.e css[b,i,j] = css[b,j,i]
def css_symmectric():
    for b in range(nCouncil):
        for i in range(nStu):
            solver.Add(css[b][i][i] == 0)
    for i in range(nStu):
        for j in range(i+1,nStu):
            for b in range(nCouncil):
                solver.Add(css[b][i][j] == css[b][j][i])
    return
#done


def css_least():
    '''
    # Each council has at least ((minStu-1)* minStu)//2 edges:
    for b in range(nCouncil):
        solver.Add(sum( sum(css[b][i][j] for j in range(i+1,nStu)) for i in range(nStu)) >= ((minStu-1)* minStu)//2)
    '''
    # Each council has at least minStu vertexs:
    for i in range(nStu):
        solver.Add(sum( sum(css[b][i][j] for j in range(nStu)) for b in range(nCouncil)) >= (minStu-1))
    return

def css_most():
    '''
    # Each council has at most (maxStu-1)*maxStu//2 edges:
    for b in range(nCouncil):
        solver.Add(sum( sum(css[b][i][j] for j in range(i+1,nStu)) for i in range(nStu)) <= ((maxStu-1)*maxStu)//2)
    '''
    # Each council has at most minStu vertexs:
    for i in range(nStu):
        solver.Add(sum( sum(css[b][i][j] for j in range(nStu)) for b in range(nCouncil)) <= (maxStu-1))
    return
'''
# The match point of two prj in a Council must be >= minMatchPrj
def css_not_the_same_council():
    for i in range(nStu):
        for j in range(i+1, nStu):
            if PrjData[i][j] < minMatchPrj:
                for b in range(nCouncil):
                    # i and j are not in the same council
                    solver.Add(css[b][i][j] == 0)
#not_the_same_council()
#done
'''
#each Council is a completed graph
def css_check_clique():
    #https://theses.hal.science/tel-01707043/document
    #page 15 in The Maximum Vertex Weight Clique Problem (MVWCP). 
    '''
    In the above document, the constraint to make sure that our output is a clique is:
    If vertex i and j are not connected then css[i] + css[j] <=1,
    which means that vertex i and vertex j CAN NOT BOTH be selected.
    It is also means that css[any edge of vertex i] + css[any edge of vertex j] <= 1,
    THEY CAN NOT BOTH BE SELECTED.
    
    DISCLAIMER:
    THIS CAN STILL RETURN A SUB GRAPH OF OUR CLIQUE, BUT DO NOT WORRY,
    THE FIRST SOLVE RETURNED IS ALWAYS THE MOST OPTIMIZATION 
    (WEIGHT OF A GRAPH > WEIGHT OF ITS SUB GRAPH)
    '''
    for i in range(nStu):
        for j in range(i+1, nStu):
            if PrjData[i][j] < minMatchPrj:
                # i and j are not connected -> i and j are not in the same council
                for b in range(nCouncil):
                    # i and j are not in the same council -> all 2 edges contain i or j on a council can not both equal to 1
                    for m in range(nStu):
                        for l in range(nStu):
                            solver.Add( css[b][i][m] + css[b][j][l] <= 1 )
                    #done
    return
#check_clique()
#done

css_once()
css_symmectric()
css_least()
css_most()
#css_not_the_same_council()
css_check_clique()

objective = solver.Objective()

#if you want to return the optimizist solution, turn this on
def get_max():
    for b in range(nCouncil):
        for i in range(nStu):
            for j in range(nStu):
                    objective.SetCoefficient(css[b][i][j], PrjData[i][j])
            for t in range(nProf):
                    objective.SetCoefficient(cst[b][i][t], PrfData[t][i])

    objective.SetMaximization()
#get_max

BeginTime = time.time()

status = solver.Solve()
if status not in [pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE]:
    print("No solution.")
    exit()

EndTime = time.time()

#print(f'Total match value: {int(objective.Value()+0.2)}')

for b in range(nCouncil):
    w("Council "+ str(b+1))
    w("Project: ", end="")
    for i in range(nStu):
        for j in range(nStu):
            if int(css[b][i][j].solution_value()) > 0:
                w(str(i+1),end =" ")
                break
    w()
    w("Teacher: ",end="")
    for t in range(nProf):
        for i in range(nStu):
            if int(cst[b][i][t].solution_value()) > 0:
                w(f"{t+1}"," ")
                break
    w("")
    '''
    for t in range(nProf):
        for i in range(nStu):
            if int(cst[b][i][t].solution_value()) > 0:
                w(f"{b} {i} {t}")
    w("")
    '''
w()
w(f"Solve in {(EndTime-BeginTime)}s")
print(f"Solve in {(EndTime-BeginTime)}s")
print("Answer in "+ fileOut)