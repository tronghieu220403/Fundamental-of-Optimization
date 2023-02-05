from ortools.sat.python import cp_model

import time

#code in line 75

class CP():
    
    def __init__(self, fileIN, fileOUT = None):
        self.fileIN = fileIN
        self.nStu = None
        self.nPrf = None
        self.nCouncil = None
        self.minStu = None
        self.maxStu = None
        self.minProf = None
        self.maxProf = None
        self.minMatchStu = None
        self.minMachProf = None
        self.PrjData = None
        self.PrfData = None
        self.fileOUT = fileOUT
        self.Guide = None
        self.finp = None
        self.BeginTime = None
        self.EndTime = None
        self.model = None
        self.ss = None
        self.st = None
        self.cs = None
        self.ct = None
        self.solver = None
        self.status = ""
        self.ans = 0
        pass
        
    def ReadInput(self):
        if type(self.fileIN) is not str or self.fileIN == "":
            raise NameError("NOT A VALID INPUT FILE.")
        
        try:
            self.finp = open(self.fileIN,"r")
        except:
            raise NameError("NOT A VALID INPUT FILE.")

        def r():
            while True:
                xx = self.finp.readline()
                if len(xx) == 1:
                    continue
                return list(map(int, xx.split()))

        self.nStu, self.nProf, self.nCouncil = map(int, self.finp.readline().split())
        self.miniStu, self.maxStu, self.miniProf, self.maxProf, self.minMatchStu, self.minMachProf = map(int, self.finp.readline().split())

        self.PrjData = [[] for i in range(self.nStu) ]

        for i in range(self.nStu):
            self.PrjData[i] = r()

        self.PrfData = [[0 for __ in range(self.nStu)] for _ in range(self.nProf) ]
        for i in range(self.nStu):
            xx = r()
            for _t in range(len(xx)):
                self.PrfData[_t][i] = xx[_t]

        self.Guide = r()
        for i in range(len(self.Guide)):
            self.Guide[i] -= 1

        for i in range(self.nStu):
            self.PrjData[i][i]= 0
        self.finp.close()
        return self.PrjData, self.PrfData

    def SetConstraints(self):
        
        self.model = cp_model.CpModel()

        #set up cs: council + student
        self.cs = [[0 for _ in range(self.nStu)] for __ in range(self.nCouncil)]
        for b in range(self.nCouncil):
            for i in range(self.nStu):
                self.cs[b][i] = self.model.NewBoolVar(f'cs_{b}_{i}')

        #set up ct: council + teacher
        self.ct = [[0 for _ in range(self.nProf)] for __ in range(self.nCouncil)]
        for b in range(self.nCouncil):
            for t in range(self.nProf):
                self.ct[b][t] = self.model.NewBoolVar(f'ct_{b}_{t}')

        def cs_once():
            #Once
            for i in range(self.nStu):
                self.model.AddExactlyOne(self.cs[b][i] for b in range(self.nCouncil))
            return
        cs_once()
        
        def ct_once():
            #Once
            for t in range(self.nProf):
                self.model.AddExactlyOne(self.ct[b][t] for b in range(self.nCouncil))
            return
        ct_once()
        
        def cs_limit():
            #Number of project in a council >= self.miniStu and <= self.maxStu
            for b in range(self.nCouncil):
                self.model.Add( sum(self.cs[b][i] for i in range(self.nStu)) >= self.miniStu)
                
            for b in range(self.nCouncil):
                self.model.Add( sum(self.cs[b][i] for i in range(self.nStu)) <= self.maxStu)
            
            return
        cs_limit()

        def ct_limit():
            #Number of teacher in a council >= self.miniProf and <= self.maxProf:
            for b in range(self.nCouncil):
                self.model.Add(sum(self.ct[b][t] for t in range(self.nProf)) >= self.miniProf)
                self.model.Add(sum(self.ct[b][t] for t in range(self.nProf)) <= self.maxProf)
            return
        ct_limit()

        def link_cs_cs():
            for b in range(self.nCouncil):
                for i in range(self.nStu):
                    for j in range(i+1,self.nStu):
                        if self.PrjData[i][j] < self.minMatchStu or self.PrjData[j][i] < self.minMatchStu:
                            self.model.AddAtMostOne([self.cs[b][i], self.cs[b][j]])
            return
        link_cs_cs()

        def link_cs_ct():
            for b in range(self.nCouncil):
                for i in range(self.nStu):
                    for t in range(self.nProf):
                        if self.PrfData[t][i] < self.minMachProf or t == self.Guide[i]:
                            self.model.AddAtMostOne([self.cs[b][i], self.ct[b][t]])
            return
        link_cs_ct()

        return

    def Solve(self, RunTime = 10.0):        
        self.solver = cp_model.CpSolver()
        #self.solver.parameters.num_search_workers = 8
        self.solver.parameters.enumerate_all_solutions = False
        self.solver.parameters.max_time_in_seconds = RunTime

        self.BeginTime = time.time()
        status = self.solver.Solve(self.model)
        self.EndTime = time.time()
        
        if status in [cp_model.UNKNOWN]:
            self.status =  "Time out."
            return 0

        if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            self.status =  "No solution."
            return 0
        
        self.status = "Solution exists."
        self.IsSolved = 1
        return 1

    def SolveHeuristic(self, RunTime = 10.0):
        self.status = None
        CP.SetConstraints(self)
        return CP.Solve(self,RunTime)

    def ChangeEF(self, e = None,f = None):
        if e!=None:
            self.minMatchStu = e
        if f!=None:
            self.minMachProf = f
        return

    def PrintAns(self, fileOUT1 = None, toCMD = True):
        def DoNothing(x):
            return
        printAns = print
        if toCMD == False:
            printAns = DoNothing
        
        if self.status != "Solution exists.":
            printAns(self.status)
            printAns("No answer!")
            return

        table = [[[] for __ in range(2)] for _ in range(self.nCouncil)]
        for b in range(self.nCouncil):
            for i in range(self.nStu):
                if int(self.solver.BooleanValue(self.cs[b][i]))>0:
                    table[b][0].append(i)
            for t in range(self.nProf):
                if int(self.solver.BooleanValue(self.ct[b][t]))>0:
                    table[b][1].append(t)

        ans = 0
        for b in range(self.nCouncil):
            for i in table[b][0]:
                for j in table[b][0]:
                    ans += self.PrjData[i][j] if i!=j else 0
                for t in table[b][1]:
                    ans += self.PrfData[t][i]
        
        printAns(f"Answer is: {ans}")
        printAns(f"Solve in {(self.EndTime-self.BeginTime)}s")

        if type(fileOUT1) is not str:
            fileOUT1 = self.fileOUT
        
        if fileOUT1 == None:
            raise NameError("NOT A VALID OUTPUT FILE.")
        
        printAns("Answer in "+ fileOUT1)

        fout = open(fileOUT1,"w")
        
        def w(x="",end='\n'):
            fout.write(format(x))
            fout.write(end)

        w(f'e and f are:')
        w(f'{self.minMatchStu} {self.minMachProf}')

        for b in range(self.nCouncil):
            w("Council "+ str(b+1))
            w("Project: ")
            for i in table[b][0]:
                w(str(i),end = " ")
            w()
            w("Teacher: ")
            for t in table[b][1]:
                w(str(t),end = " ")
            w()
            w()

        w()
        w(f"Answer is: {ans}")
        w(f"Solve in {(self.EndTime-self.BeginTime)}s")
        fout.close()
        self.ans = ans
        return ans

    def GetRunTime(self):
        return self.EndTime-self.BeginTime
    
    def GetValue(self,x):
        try:
            return eval("self."+x)
        except:
            raise ValueError("Not thing named " + x)
        
from random import *
import time
import os

def r(x,y=0):
    if y>x:
        x,y = y,x
    return randint(y,x)


BeginTime = time.time()

finp = 0
def read():
    global finp
    while True:
        xx = finp.readline()
        if "No" in xx:
            print("No solution.")
            #exit()
        if len(xx) == 1 or "C" in xx or ":" in xx or "i" in xx:
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
    for _ in range(3):
        finp.readline()
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
                        finp.close()
                        raise ValueError(f'Wrong in StuData: {i} {j}: {StuData[i-1][j-1]} < {e}')
            for t in Prf:
                ans+= PrfData[t-1][i-1]
                if PrfData[t-1][i-1] < f:
                    finp.close()
                    raise ValueError(f'Wrong in PrfData: {t} {i}: {PrfData[t-1][i-1]} < {f}')
    finp.close()
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


def CheckHeuristic(Gen = 0,nTest = 1, _N = 1000, _M = 1000, _K = 50):

    def CheckOnlyHeuristic(_N,_M,x=0,fileOut = "",fileIn = "data.inp"):
        ans3 = 0
        if x==1:
            BeginTime = time.time()
            os.system("Heuristic.exe")           #write answer to HeuristicAns.out
            os.system("Heuristic1.exe")          #write answer to HeuristicAns1.out
            #print(f"Solve in {time.time()-BeginTime}s.")
            if _N*(_N+_M) <= 150*300:
                os.popen("python HeuristicSolverForSmallData.py").read()   #write answer to HeuristicAns2.out
                ans3 = check("HeuristicAns2.out")
                if ans3 == -1:
                    print("HeuristicSolverForSmallData.py wrong answer.")
        ans1 = check("HeuristicAns.out")
        ans2 = check("HeuristicAns1.out")
        if ans1 == -1:
            print("Heuristic.exe provide no solution")
        if ans2 == -1:
            print("Heuristic1.exe provide no solution")
        if ans3 == -1:
            print("HeuristicSolverForSmallData.py provide no solution")
        if ans2 == max([ans1,ans2,ans3]):
            print("Answer in HeuristicAns1.out")
        elif ans1 == max([ans1,ans2,ans3]):
            print("Answer in HeuristicAns.out")
        elif ans3 == max([ans1,ans2,ans3]):
            print("Answer in HeuristicAns2.out")

    #Generate input to data.inp and check the result.
    Test = nTest
    for _ in range(Test):
        if nTest >= 2:
            print("Test case "+str(_))
        T = Gen
        while(T):
            if Generate(_N,_M,_K)==1:
                break
        CheckOnlyHeuristic(_N,_M,1) #if you already have an input file "data.inp", you can check your code with that test case by using this.


def CheckTrue(Gen = 0,nTest = 1, _N = 15, _M = 10, _K = 3):

    def CheckOnlyTrue(_N,_M,x=0,fileOut = "",fileIn = "data.inp"):
        if x==1:
            BeginTime = time.time()
            os.system("python Correct_CP_SAT_Solver.py")
        check( "CorrectAns.out")

    Test = nTest
    for _ in range(Test):
        if nTest >= 2:
            print("Test case "+str(_))
        T = Gen
        while(T):
            if Generate(_N,_M,_K)==1:
                break
        CheckOnlyTrue(_N,_M,1) #if you already have an input file "data.inp", you can check your code with that test case by using this.