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

        self.PrfData = [[] for i in range(self.nProf) ]

        for i in range(self.nProf):
            self.PrfData[i] = r()

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

    def Solve(self, RunTime = 60.0):        
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

    def SolveHeuristic(self, RunTime = 60.0):
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
                if int(self.solver.Value(self.cs[b][i]))>0:
                    table[b][0].append(i)
            for t in range(self.nProf):
                if int(self.solver.Value(self.ct[b][t]))>0:
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
        
        
class Greedy():
        
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

        self.PrfData = [[] for i in range(self.nProf) ]

        for i in range(self.nProf):
            self.PrfData[i] = r()

        self.Guide = r()
        for i in range(len(self.Guide)):
            self.Guide[i] -= 1

        for i in range(self.nStu):
            self.PrjData[i][i]= 0
        self.finp.close()
        return self.PrjData, self.PrfData

