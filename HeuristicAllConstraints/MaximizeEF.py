from Project26Heuristic import CP
from itertools import chain
import time
a = CP("1.inp")

from bisect import *

StuData, PrfData = a.ReadInput()

StuData = list(sorted(list(set(list(chain.from_iterable(StuData))))))
PrfData = list(sorted(list(set(list(chain.from_iterable(PrfData))))))

eleft = 0
fleft = 0

fright = len(PrfData)-1
eright = len(StuData)-1
mid = 0

if(a.SolveHeuristic()==1):
    eleft = bisect_right(StuData,a.minMatchStu)-1
    fleft = bisect_right(StuData,a.minMachProf)-1
    print("There exists a solution for default e and f of the teacher's data.")
else:
    print("There exists no solution for default e and f of the teacher's data.")
    
a.PrintAns("1.out")

print("______________________________________________")
print("Now maximize e and f.")

emax = -1

RunTime = 0

while(eleft<=eright):
    mid = (eleft+eright)//2
    a.ChangeEF(StuData[mid])
    if a.SolveHeuristic(2)==1:
        emax = max(emax,mid)
        eleft = mid + 1
    else:
        eright = mid - 1
    RunTime += a.GetRunTime()

if emax == -1:
    print("No more optimal solution")
    open("2.out","w").write("No more optimal solution")
    print("______________________________________________")
    exit()

fmax = -1
    
while(fleft<=fright):
    mid = (fleft+fright)//2
    a.ChangeEF(StuData[emax], PrfData[mid])
    if a.SolveHeuristic(5)==1:
        a.PrintAns("2.out",toCMD = False)
        fmax = max(fmax,mid)
        fleft = mid + 1
    else:
        fright = mid - 1
    RunTime += a.GetRunTime()

if fmax == -1:
    print("No more optimal solution")
    open("2.out","w").write("No more optimal solution")
    print("______________________________________________")
    exit()

print(f'Maximize value of e is {StuData[emax]}')
print(f'Maximize value of f is {PrfData[fmax]}')
print("Answer in 2.out")

print("Solve in " + str(RunTime) +"s")

print("______________________________________________")
