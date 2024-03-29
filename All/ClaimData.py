from random import *
from Project26Ex import CP
def r(x,y=0):
    if y>x:
        y,x = x,y
    return randint(y,x)

from ortools.sat.python import cp_model

import time

BeginTime = time.time()

import os


def read(finp):
    while True:
        xx = finp.readline()
        if "No" in xx:
            #print("No solution.")
            finp.close()
            return -1
        if len(xx) == 1 or "C" in xx or ":" in xx:
            continue
        return list(map(int, xx.split()))

def Generate(nStu, nProf, nCouncil):
    
    model = cp_model.CpModel()

    Guide = [0 for _ in range(nStu)]

    minStu = max(max(nStu//nCouncil*3//4,r(nStu//nCouncil- (r(max(nStu//nCouncil-2,1),1))//2,2)),1)
    maxStu = minStu + r(max(2,nStu-nCouncil*minStu), 2)
    
    minProf = max(max(nProf//nCouncil*3//4,r(nProf//nCouncil- (r(max(nProf//nCouncil-2,1),1)//2),2)),1)
    maxProf = minProf + r(max(2,nProf-nCouncil*minProf),2)

    nCS = [0 for _  in range(nCouncil)]
    nCT = [0 for _  in range(nCouncil)]
    
    for i in range(nCouncil):
        nCS[i] = model.NewIntVar(minStu,maxStu,f"x_{i}")
        nCT[i] = model.NewIntVar(minProf,maxProf,f"y_{i}")
    
    model.Add(sum(nCS)==nStu)
    model.Add(sum(nCT)==nProf)

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

    stubase = 0
    prfbase = 0

    for b in range(nCouncil):
        for i in range(solver.Value(nCS[b])):
            for j in range(i+1,solver.Value(nCS[b])):
                ss[i+stubase][j+stubase] = 1
                ss[j+stubase][i+stubase] = 1
            for t in range(solver.Value(nCT[b])):
                st[i+stubase][t+prfbase] = 1
        stubase += solver.Value(nCS[b])
        prfbase += solver.Value(nCT[b])

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
            else:
                Guide[i] = t
                if j!=Guide[i]:
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
    
    fout = open("data.inp","w")
    def w(x="", end = '\n'):
        fout.write(format(x))
        fout.write(end)
        return

    w(str(nStu) + " " + str(nProf) + " " + str(nCouncil))
    minMatchPrj = r(1500,500)
    minMatchPrf = r(1500,500)
    w(str(minStu) + " " + str(maxStu) + " " + str(minProf) + " " + str(maxProf) + " " + str(minMatchPrj) + " " + str(minMatchPrf))
    
    for i in range(nStu):
        for j in range(nStu):
            if table[i][j] > 0:
                w(minMatchPrj+r(minMatchPrj)+10,end = " ")
                #w(9, end = " ")
            else:
                w(minMatchPrj-r(minMatchPrj)//2+10, end = " ")
                #w(0, end = " ")
        w()
    w()
    for t in range(nProf):
        for i in range(nStu):
            if table1[t][i] == 0:
                w(minMatchPrf-r(minMatchPrf//2)+10,end = " ")
                #w(0,end=" ")
            else:
                w(minMatchPrf+r(minMatchPrf)+10,end = " ")
                #w(9,end=" ")
        w()
    w()
    for i in range(nStu):
        w(Guide[i]+1,end = " ")
    w()
    fout.close()

    #print("Generated.",flush=True)

    return 1

def check(fileOut,fileIn = "data.inp"):
    #print("Checking your answer...")
    finp = open(fileOut,"r")
    x = CP(fileIn)
    StuData, PrfData = x.ReadInput()
    l = read(finp)
    if l == -1:
        return ["N/A" for _ in range(4)]
    #print(l)
    e, f = l[0],l[1]
    nCouncil = x.GetValue("nCouncil")
    nStu = x.GetValue("nStu")
    nProf = x.GetValue("nProf")
    StuData1 = [0 for _ in range(nCouncil)]
    PrfData1 = [0 for _ in range(nCouncil)]
    ans = 0
    for b in range(nCouncil):
        Stu = read(finp)
        Prf = read(finp)
        StuData1[b] = Stu
        PrfData1[b] = Prf
        for i in Stu:
            for j in Stu:
                if i!=j:
                    ans += StuData[i-1][j-1]
                    if StuData[i-1][j-1] < e:
                        raise ValueError(f'Wrong in StuData: {i} {j}: {StuData[i-1][j-1]} < {e}')
            for t in Prf:
                ans += PrfData[t-1][i-1]
                if PrfData[t-1][i-1] < f:
                    raise ValueError(f'Wrong in PrfData: {t} {i}: {PrfData[t-1][i-1]} < {f}')

    for i in range(nCouncil):
        for j in range(i+1,nCouncil):
            if len(set(StuData1[i]).intersection(set(StuData1[j]))) != 0:
                raise ValueError(f'Student in 2 council: {i} {j}')
            if len(set(PrfData1[i]).intersection(set(PrfData1[j]))) != 0:
                raise ValueError(f'Teacher in 2 council: {i} {j}')
    
    if sum(len(StuData1[i]) for i in range(nCouncil))!=nStu:
        raise ValueError(f'Not enough student: {sum(len(StuData1[i]) for i in range(nCouncil))} {nStu}')
    if sum(len(PrfData1[i]) for i in range(nCouncil))!=nProf:
        raise ValueError(f'Not enough teacher: {sum(len(PrfData1[i]) for i in range(nCouncil))} {nProf}')

    #print("No error found.")
    while(True):
        xx = finp.readline()
        if "in" in xx:
            finp.close()
            return [e, f, ans, xx[len("Solve in "):-1]]  
    

def get_ans(fileOut,fileIn = "data.inp"):
    finp1 = open(fileOut,"r")
    while(True):
        xx = finp1.readline()
        if ("o s" in xx):
            return -1
        if "wer" in xx:
            return int(xx[len("Answer is: "):-1])

def CheckOnlyHeu(_N,_M,x=0,fileOut = "",fileIn = "data.inp"):
    ans3 = 0
    if x==1:
        BeginTime = time.time()
        os.system("Heuristic.exe")           #write answer to HeuristicAns.out
        os.system("Heuristic1.exe")          #write answer to HeuristicAns1.out
        os.system("Heuristic3.exe")          #write answer to HeuristicAns3.out
        #print(f"Solve in {time.time()-BeginTime}s.")
        if _N*(_N+_M) <= 150*300:
            os.popen("python HeuristicSolverForSmallData.py").read()   #write answer to HeuristicAns2.out
            ans3 = check("HeuristicAns2.out")
    #ans1 = check(fileOut,fileIn)
    #ans2 = check("HeuristicAns1.out",fileIn)
    ans1 = check("HeuristicAns.out")
    ans2 = check("HeuristicAns1.out")
    ans4 = check("HeuristicAns3.out")
    '''
    if ans2 == max([ans1,ans2,ans3,ans4]):
        print("Answer in HeuristicAns1.out")
    elif ans1 == max([ans1,ans2,ans3,ans4]):
        print("Answer in HeuristicAns.out")
    elif ans3 == max([ans1,ans2,ans3,ans4]):
        print("Answer in HeuristicAns2.out")
    elif ans4 == max([ans1,ans2,ans3,ans4]):
        print("Answer in HeuristicAns3.out")
    '''

def CheckOnlyCP(x=0,fileOut = "CorrectAns.out",fileIn = "data.inp"):
    if x==1:
        BeginTime = time.time()
        os.popen("python Correct_CP_SAT_Solver.py").read()
        #print(f"Solve in {time.time()-BeginTime}s.")
    return check(fileOut,fileIn)


#Generate input to data.inp and check the result.
#GenerateAndCheck(30,500,500) #n and m are number of students and number of teachers
Test = 100

wData = open("RunData.out","w")

import math

for _ in range(10,18):
    print("Test case "+str(_))
    _N = _
    _M = _
    if _N <=100:
        _K = r(int(math.sqrt(_N)),int(math.sqrt(_N)))
    else:
        _K = r(int(math.sqrt(_N))//10*10-5,int(math.sqrt(_N))//10*10+5)
    while(True):
        if Generate(_N,_M,_K)==1:
            break
    h = CheckOnlyHeu(_N,_M,1)
    if "N/A" == h[0]:
        wData.write(f"{_N},{_M},{_K},N/A,N/A,N/A,N/A,N/A,N/A,N/A,N/A,N/A,N/A,N/A\n")
        wData.flush()
        continue
    if _N <= 20 and _M <=20:
        t = CheckOnlyCP(1)
    else:
        t = ["N/A" for _ in range(4)]
    if "N/A" == t[0]:
        wData.write(f"{_N},{_M},{_K},N/A,N/A,N/A,N/A,{h[0]},{h[1]},{h[2]},N/A,N/A,N/A,,{h[3]}\n")
    else:
        wData.write(f"{_N},{_M},{_K},{t[0]},{t[1]},{t[2]},{t[3]},{h[0]},{h[1]},{h[2]},{h[0]/t[0]},{h[1]/t[1]},{h[2]/t[2]},{h[3]}\n")
    wData.flush()
    #if you already have an input file "data.inp", you can check your code with that test case by using this.

for _ in range(1,Test+1):
    print("Test case "+str(_*10))
    _N = 10*_
    _M = 10*_
    if _N <=100:
        _K = r(int(math.sqrt(_N)),int(math.sqrt(_N)))
    else:
        _K = r(int(math.sqrt(_N))//10*10-5,int(math.sqrt(_N))//10*10+5)
    while(True):
        if Generate(_N,_M,_K)==1:
            break
    h = CheckOnlyHeu(_N,_M,1)
    if "N/A" == h[0]:
        wData.write(f"{_N},{_M},{_K},N/A,N/A,N/A,N/A,N/A,N/A,N/A,N/A,N/A,N/A,N/A\n")
        wData.flush()
        continue
    if _N <= 20 and _M <=20:
        t = CheckOnlyCP(1)
    else:
        t = ["N/A" for _ in range(4)]
    if "N/A" == t[0]:
        wData.write(f"{_N},{_M},{_K},N/A,N/A,N/A,N/A,{h[0]},{h[1]},{h[2]},N/A,N/A,N/A,{h[3]}\n")
    else:
        wData.write(f"{_N},{_M},{_K},{t[0]},{t[1]},{t[2]},{t[3]},{h[0]},{h[1]},{h[2]},{h[0]/t[0]},{h[1]/t[1]},{h[2]/t[2]},{h[3]}\n")
    wData.flush()
    #if you already have an input file "data.inp", you can check your code with that test case by using this.
