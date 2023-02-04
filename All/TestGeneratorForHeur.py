from random import *
from Project26Ex import CP
def r(x,y=0):
    if y>x:
        x,y = y,x
    return randint(y,x)

from ortools.sat.python import cp_model

import time

BeginTime = time.time()

import os

finp = 0#open("HeuristicAns.out","r")

def read():
    global finp
    while True:
        xx = finp.readline()
        if "No" in xx:
            print("No solution.")
            #exit()
        if len(xx) == 1 or "C" in xx or ":" in xx:
            continue
        return list(map(int, xx.split()))

def Generate(nStu, nProf, nCouncil):
    
    model = cp_model.CpModel()

    Guide = [0 for _ in range(nStu)]

    minStu = max(nStu//nCouncil*3//4,r(nStu//nCouncil- (r(max(nStu//nCouncil-2,1),1))//2,2))
    maxStu = minStu + r(max(2,nStu-nCouncil*minStu), 2)
    
    minProf = max(nProf//nCouncil*3//4,r(nProf//nCouncil- (r(max(nProf//nCouncil-2,1),1)//2),2))
    maxProf = minProf + r(max(2,nProf-nCouncil*minProf),2)
    table = [[0 for __ in range(nStu)] for _ in range(nStu)]
    table1 = [[0 for __ in range(nStu)] for _ in range(nProf)]
     
    fout = open("data.inp","w")
    def w(x="", end = '\n'):
        fout.write(format(x))
        fout.write(end)
        return

    w(str(nStu) + " " + str(nProf) + " " + str(nCouncil))
    #minMatchPrj = r(15000000,500)
    #minMatchPrf = r(15000000,500)
    minMatchPrf  = 1
    minMatchPrj = 1
    w(str(minStu) + " " + str(maxStu) + " " + str(minProf) + " " + str(maxProf) + " " + str(minMatchPrj) + " " + str(minMatchPrf))
    
    for i in range(nStu):
        for j in range(nStu):
            if table[i][j] > 0:
                #w(minMatchPrj+r(minMatchPrj)+10,end = " ")
                w(r(9,1), end = " ")
            else:
                #w(minMatchPrj-r(minMatchPrj)//2+10, end = " ")
                w(r(9,1), end = " ")
        w()
    w()
    for i in range(nStu):
        for t in range(nProf):
            if table1[t][i] == 0:
                #w(minMatchPrf-r(minMatchPrf//2)+10,end = " ")
                w(r(9,1),end=" ")
            else:
                #w(minMatchPrf+r(minMatchPrf)+10,end = " ")
                w(r(9,1),end=" ")
        w()
    dem = 0
    index = 0
    Guide = [i%nProf for i in range(nStu)]
    shuffle(Guide)

    for i in range(nStu):
        w(Guide[i]+1,end = " ")
    w()
    fout.close()

    return 1

def check(fileOut,fileIn = "data.inp"):
    global finp 
    finp = open(fileOut,"r")
    if ("o s" in finp.readline()):
        return -1
    x = CP(fileIn)
    StuData, PrfData = x.ReadInput()
    e, f = x.GetValue("minMatchStu"),x.GetValue("minMachProf")
    nCouncil = x.GetValue("nCouncil")
    nStu = x.GetValue("nStu")
    nProf = x.GetValue("nProf")
    StuData1 = [0 for _ in range(nCouncil)]
    PrfData1 = [0 for _ in range(nCouncil)]
    ans = 0
    for b in range(nCouncil):
        Stu = read()
        Prf = read()
        StuData1[b] = Stu
        PrfData1[b] = Prf
        for i in Stu:
            for j in Stu:
                if i!=j:
                    ans += StuData[i-1][j-1]
                    if StuData[i-1][j-1] < e:
                        raise ValueError(f'Wrong in StuData: {i} {j}: {StuData[i-1][j-1]} < {e}')
            for t in Prf:
                ans+= PrfData[i-1][j-1]
                if PrfData[t-1][i-1] < f:
                    raise ValueError(f'Wrong in PrfData: {t} {i}: {PrfData[t-1][i-1]} < {f}')
    #finp.close()
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
    return ans

def get_ans(fileOut,fileIn = "data.inp"):
    finp1 = open(fileOut,"r")
    while(True):
        xx = finp1.readline()
        if ("o s" in xx):
            return -1
        if "wer" in xx:
            return int(xx[len("Answer is: "):-1])

def CheckOnly(_N,_M,x=0,fileOut = "",fileIn = "data.inp"):
    ans3 = 0
    if x==1:
        BeginTime = time.time()
        os.system("Heuristic.exe")  #write answer to HeuristicAns.out
        os.system("Heuristic1.exe")          #write answer to HeuristicAns1.out
        os.system("Heuristic3.exe")          #write answer to HeuristicAns3.out
        #print(f"Solve in {time.time()-BeginTime}s.")
        if _N*(_N+_M) <= 150*300:
            os.popen("python HeuristicSolverForSmallData.py").read()   #write answer to HeuristicAns2.out
            ans3 = get_ans("HeuristicAns2.out")
    #ans1 = check(fileOut,fileIn)
    #ans2 = check("HeuristicAns1.out",fileIn)
    ans1 = get_ans("HeuristicAns.out")
    ans2 = get_ans("HeuristicAns1.out")
    ans4 = get_ans("HeuristicAns3.out")
    if ans1 == -1:
        print("Heuristic.exe provide no solution")
    if ans2 == -1:
        print("Heuristic1.exe provide no solution")
    if ans3 == -1:
        print("HeuristicSolverForSmallData.py provide no solution")
    if ans4 == -1:
        print("Heuristic3.exe provide no solution")
    if ans2 == max([ans1,ans2,ans3,ans4]):
        print("Answer in HeuristicAns1.out")
    elif ans1 == max([ans1,ans2,ans3,ans4]):
        print("Answer in HeuristicAns.out")
    elif ans3 == max([ans1,ans2,ans3,ans4]):
        print("Answer in HeuristicAns2.out")
    elif ans4 == max([ans1,ans2,ans3,ans4]):
        print("Answer in HeuristicAns3.out")


#Generate input to data.inp and check the result.
Test = 1
for _ in range(Test):
    print("Test case "+str(_))
    _N = 1000
    _M = 1000
    _K = r(50,70)
    T = 0
    while(T):
        if Generate(_N,_M,_K)==1:
            break
    #CheckOnly(_N,_M,1) #if you already have an input file "data.inp", you can check your code with that test case by using this.
