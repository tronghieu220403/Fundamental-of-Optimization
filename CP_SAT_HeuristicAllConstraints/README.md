File:

+) Project26Heuristic is a library where our main code saved.

+) MaximizeEF is to maximize last constraints of the project.

+) TestGenerator will generate test cases + check your answer or check you answer only.

So, in this case, we came to some simple conclusion to improve runtime of the heuristic:

1) No more need ss[i][j], st[i][j]:

+) If cs[b,i] == 1 and cs[b,j] == 1 mean that i and j are in the same council, this is only use to calculate the result so we don't need ss[i][j] = 1 to store them.

+) Similary to st[i,t]

2) No more need link_cs_cs_ss() and link_cs_ct_cs():

+) We have a conclusion: If i and j can be connected, they must be in the in different council -> All the students in a same council can be connected with each others.

+) Similary to i and t.

So we only need:


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