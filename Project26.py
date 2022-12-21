from ortools.sat.python import cp_model

import time

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
        self.sPrfData = None
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
        self.IsSolved = 0
        self.IsInputed = 0
        self.IsConstrainted = 0
        self.IsSolveMax = 0
        self.status = ""
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
        
        self.IsInputed = 1
        return
    
    def SetConstraints(self):
        
        print(self.minMatchStu)
        
        if self.IsInputed == 0:
            CP.ReadInput(self)
        
        self.model = cp_model.CpModel()

        #set up cs: council + student
        self.cs = [[0 for _ in range(self.nStu)] for __ in range(self.nCouncil)]

        for b in range(self.nCouncil):
            for i in range(self.nStu):
                self.cs[b][i] = self.model.NewBoolVar(f'cs_{b}_{i}')

        def cs_once():
            #Once
            for i in range(self.nStu):
                self.model.Add( sum(self.cs[b][i] for b in range(self.nCouncil)) == 1)
            return
        cs_once()

        def cs_limit():
            #Number of project in a council >= self.miniStu and <= self.maxStu
            for b in range(self.nCouncil):
                self.model.Add( sum(self.cs[b][i] for i in range(self.nStu)) >= self.miniStu)
                
            for b in range(self.nCouncil):
                self.model.Add( sum(self.cs[b][i] for i in range(self.nStu)) <= self.maxStu)
            
            return
        cs_limit()

        #set up ct: council + teacher
        self.ct = [[0 for _ in range(self.nProf)] for __ in range(self.nCouncil)]
        for b in range(self.nCouncil):
            for t in range(self.nProf):
                self.ct[b][t] = self.model.NewBoolVar(f'ct_{b}_{t}')

        def ct_once():
            #Once
            for t in range(self.nProf):
                self.model.Add(sum(self.ct[b][t] for b in range(self.nCouncil)) == 1)
            return
        ct_once()

        def ct_limit():
            #Number of teacher in a council >= self.miniProf and <= self.maxProf:
            for b in range(self.nCouncil):
                self.model.Add(sum(self.ct[b][t] for t in range(self.nProf)) >= self.miniProf)
                self.model.Add(sum(self.ct[b][t] for t in range(self.nProf)) <= self.maxProf)
            return
        ct_limit()

        #set up ct: student + teacher
        self.st = [[0 for _ in range(self.nProf)] for __ in range(self.nStu)]
        for i in range(self.nStu):
            for t in range(self.nProf):
                self.st[i][t] = self.model.NewBoolVar(f'st_{i}_{t}')

        def st_set_up():
            for i in range(self.nStu):
                for t in range(self.nProf):
                    if self.PrfData[t][i] < self.minMachProf:
                        self.model.Add(self.st[i][t] == 0)

            for i in range(len(self.Guide)):
                self.model.Add(self.st[i][self.Guide[i]] == 0)

            return
        st_set_up()

        def st_limit():
            #Number of teacher that a student can meet in his council >= self.miniProf and <= self.maxProf:
            for i in range(self.nStu):
                self.model.Add(sum(self.st[i][t] for t in range(self.nProf)) >= self.miniProf)
                self.model.Add(sum(self.st[i][t] for t in range(self.nProf)) <= self.maxProf)
            #Number of student that a teacher can meet in his council >= self.miniProf and <= self.maxProf:
            for t in range(self.nProf):
                self.model.Add(sum(self.st[i][t] for i in range(self.nStu)) >= self.miniStu)
                self.model.Add(sum(self.st[i][t] for i in range(self.nStu)) <= self.maxStu)

            return
        st_limit()

        #set up ss: student + student
        self.ss = [[0 for _ in range(self.nStu)] for __ in range(self.nStu)]
        for i in range(self.nStu):
            for j in range(self.nStu):
                self.ss[i][j] = self.model.NewBoolVar(f'ss_{i}_{j}')

        def ss_set_up():
            print(self.minMatchStu)
            for i in range(self.nStu):
                self.model.Add(self.ss[i][i] == 0)
                for j in range(self.nStu):
                    if self.PrjData[i][j] < self.minMatchStu:
                        self.model.Add(self.ss[i][j] == 0)
            return
        ss_set_up()

        def ss_symmetric():
            for i in range(self.nStu):
                for j in range(i+1,self.nStu):
                    self.model.Add(self.ss[i][j]==self.ss[j][i])
            return
        ss_symmetric()

        def ss_limit():
            for i in range(self.nStu):
                self.model.Add(sum(self.ss[i][j] for j in range(self.nStu)) >= self.miniStu-1)
                self.model.Add(sum(self.ss[i][j] for j in range(self.nStu)) <= self.maxStu-1)
            return
        ss_limit()

        def link_cs_ss():
            for b in range(self.nCouncil):
                for i in range(self.nStu):
                    for j in range(i+1,self.nStu):
                        self.model.Add(self.cs[b][i] + self.cs[b][j] <= self.ss[i][j] +1)
            return
        link_cs_ss()

        def link_cs_ct_st():
            for b in range(self.nCouncil):
                for i in range(self.nStu):
                    for t in range(self.nProf):
                        self.model.Add(self.cs[b][i] + self.ct[b][t] <= self.st[i][t] + 1)
            return
        link_cs_ct_st()        
        
        self.IsConstrainted = 1

        return

    def Maximize(self):
        if self.IsConstrainted == 0:
            CP.SetConstraints(self)
        
        objective = []
        for i in range(self.nStu):
            for j in range(self.nStu):
                objective.append(cp_model.LinearExpr.Term(self.ss[i][j], self.PrjData[i][j]))
            for t in range(self.nProf):
                objective.append(cp_model.LinearExpr.Term(self.st[i][t], self.PrfData[t][i]))

        # Maximize total value of packed items.
        self.model.Maximize(cp_model.LinearExpr.Sum(objective))
        self.IsSolveMax = 1
        return

    def Solve(self, RunTime = 3600.0*24):
        if self.IsConstrainted == 0:
            CP.SetConstraints(self)

        print("SOLVING!",flush=True)
        
        self.solver = cp_model.CpSolver()
        
        if self.IsSolveMax == 0:
            self.solver.parameters.enumerate_all_solutions = False
        else:
            self.solver.parameters.enumerate_all_solutions = True

        self.solver.parameters.max_time_in_seconds = RunTime

        self.BeginTime = time.time()
        status = self.solver.Solve(self.model)
        self.EndTime = time.time()
        
        print("FINISH!",flush=True)
        
        if status in [cp_model.UNKNOWN]:
            self.status =  "Time out."
            return 0

        if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            self.status =  "No solution."
            return 0
        
        self.IsSolved = 1
        return 1

    def SolveHeuristic(self, RunTime = 3600.0*24):
        if self.IsSolveMax == 1 or self.IsConstrainted == 0:
            CP.SetConstraints(self)
            self.IsSolveMax = 0
        
        self.IsSolved = 1

        return CP.Solve(self,RunTime)

    def SolveMax(self, RunTime = 3600.0*24):
        if self.IsConstrainted == 0:
            CP.SetConstraints(self)

        if self.IsSolveMax == 0:
            CP.Maximize(self)
        
        self.IsSolved = 1
        return CP.Solve(self,RunTime)
    
    def Change_e_f(self, e = None,f = None):
        if e!=None:
            self.minMatchStu = e
            print(self.minMatchStu)
        if f!=None:
            self.minMachProf = f
        self.IsConstrainted = 0
        self.IsSolveMax = 0
        self.IsSolved = 0
        return

    def PrintAns(self, fileOUT1 = None):
        if self.IsInputed == 0:
            raise SyntaxError("Not input yet!")
        if self.IsSolved == 0:
            raise SyntaxError("Not solve yet!")
        
        if self.status != "":
            print(self.status)
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
        
        print(f"Answer is: {ans}")
        print(f"Solve in {(self.EndTime-self.BeginTime)}s")

        if type(fileOUT1) is not str:
            fileOUT1 = self.fileOUT
        
        if fileOUT1 == None:
            raise NameError("NOT A VALID OUTPUT FILE.")
        
        print("Answer in "+ fileOUT1)

        fout = open(fileOUT1,"w")
        
        def w(x="",end='\n'):
            fout.write(format(x))
            fout.write(end)


        for b in range(self.nCouncil):
            w("Council "+ str(b+1))
            w("Project: ")
            for i in range(self.nStu):
                if int(self.solver.Value(self.cs[b][i]))>0:
                    w(str(i),end = " ")
            w()
            w("Teacher: ")
            for t in range(self.nProf):
                if int(self.solver.Value(self.ct[b][t]))>0:
                    w(str(t),end = " ")
            w()
            w()

        w()
        w(f"Answer is: {ans}")
        w(f"Solve in {(self.EndTime-self.BeginTime)}s")
        
        return