#include <bits/stdc++.h>

using namespace std;

#define el '\n'

#define int long long

typedef long long ll;

typedef unsigned long long ull;

typedef long double ld;

const int MaxN = 1e6+1e5;

const ll mod = 1e9+7;

int debug;

struct Node
{
    int prev;
    int next;
};

int del(vector<Node> &a, int id)
{
    if(a[id].prev==0&&a[id].next<=id)
        return 0;
    a[a[id].prev].next = a[id].next;
    a[a[id].next].prev = a[id].prev;
    a[id].next = 0;
    a[id].prev = 0;
    return 1;
}

int ins(vector<Node> &target, vector<int> &source)
{
    int sz = source.size();
    if(sz==0)
        target[0].next = 1004;
    else
        target[0].next = source[0];
    for(int i=0;i<sz;i++)
    {
        if(i==0)
            target[source[i]].prev = 0;
        else
            target[source[i]].prev = source[i-1];
        if(i==sz-1)
            target[source[i]].next = 1004;
        else
            target[source[i]].next = source[i+1];
    }
    return sz;
}

struct Council
{
    vector<int> t,s;
    vector<Node> ps;
    vector<Node> pt;
    int ps_sz;
    int pt_sz;
};

Council c[1104];

struct info
{
    int nStu,nProf,nC;
    int minStu, maxStu, minProf, maxProf, minMatchStu, minMatchProf;
    int prj[1104][1104], prf[1104][1104];
    int g[1104];
};

info g;

//double linked list
struct dll
{
    vector<Node> s;
    vector<Node> t;
    int ssz,tsz;
};

dll t[1104],s[1104];

int intersection(vector<Node> &p,vector<Node> &pa)
{
    int ans = 0;
    int now1 = 0;
    while(p[now1].next!=1004&&p[now1].next!=0)
    {
        int val = p[now1].next;
        if(pa[val].next!=0)
            ans++;
        now1 = p[now1].next;
    }
    return ans;
}

vector<Node> pt;
vector<Node> ps;

int ps_sis[1100];
int pt_sit[1100];
int ps_tts[1100];

int pts_s[1100]; // potential sum of a student
int pts_t[1100]; // potential sum of a teacher

int sum_cs[1100][1100]; // sum_cs[c][i]: sum of student i to a council c
int sum_ct[1100][1100]; // sum_ct[c][t]: sum of teacher t to a council c

int FindArbitrarySolution(int MethodFlag, int BSF)
{
    // set up data
    fill(ps_sis,ps_sis+1050,0);
    fill(pt_sit,pt_sit+1050,0);
    fill(ps_tts,ps_tts+1050,0);
    fill(pts_s,pts_s+1050,0);
    fill(pts_t,pts_t+1050,0);

    for(int i=0;i<1100;i++)
    {
        for (int j=0;j<1100;j++)
        {
            sum_cs[i][j] = 0;
            sum_ct[i][j] = 0;
        }
    }

    for(int i=1;i<=g.nStu;i++)
    {
        s[i].t.clear();
        s[i].t.resize(1100);
        s[i].s.clear();
        s[i].s.resize(1100);
        s[i].ssz = 0;
        s[i].tsz = 0;
        memset(&s[i].s[0],0,1100*sizeof(Node));
        memset(&s[i].t[0],0,1100*sizeof(Node));
    }
    for(int _t=1;_t<=g.nProf;_t++)
    {
        t[_t].s.clear();
        t[_t].s.resize(1100);
        t[_t].ssz = 0;
        memset(&t[_t].s[0],0,1100*sizeof(Node));
    }
    //end set up data

    /*
    Setting up double linked list for s[i].s, s[i].t, t[_t].s
    */
    vector<int> StudentList,TeacherList;
    for(int i=1;i<=g.nStu;i++)
    {
        for(int j=1;j<=g.nStu;j++)
        {
            // if student i and student j have a possibility to be in a same group
            if (g.prj[i][j]>=g.minMatchStu&& g.prj[j][i]>=g.minMatchStu)
            {
                StudentList.push_back(j);
            }
        }
        // s[i].s: List of potential student that can be in same council with student i
        s[i].ssz = ins(s[i].s,StudentList);
        for (int _t=1;_t<=g.nProf;_t++)
        {
            // if student i and teacher t have a possibility to be in a same group
            if (g.prf[_t][i]>=g.minMatchProf)
            {
                TeacherList.push_back(_t);
            }
        }
        //s[i].t: List of potential teacher that can be in same council with student i
        s[i].tsz = ins(s[i].t,TeacherList);
        TeacherList.clear();
        StudentList.clear();
    }
    for (int _t=1;_t<=g.nProf;_t++)
    {
        for (int i=1;i<=g.nStu;i++)
        {
            // if student i and teacher _t have a possibility to be in a same group
            if (g.prf[_t][i]>=g.minMatchProf)
            {
                StudentList.push_back(i);
            }
        }
        //t[_t].s: List of potential student that can be in same council with teacher _t
        t[_t].ssz = ins(t[_t].s,StudentList);
        StudentList.clear();
    }

    //set up data
    pt.clear();ps.clear();

    int StudentSelected[1100],TeacherSelected[1100];
    // StudentSelected[i] = 1 means that student i (project i) was selected
    // TeacherSelected[_t] = 1 means that teacher _t was selected
    fill(StudentSelected,StudentSelected+1050,0);
    fill(TeacherSelected,TeacherSelected+1050,0);
    int ps_sz = 0; //potential student size
    int pt_sz = 0; //potential teacher size

    for(int _c=1;_c<=g.nC;_c++)
    {
        c[_c].ps.clear();
        c[_c].pt.clear();
        c[_c].s.clear();
        c[_c].t.clear();
        c[_c].ps_sz = 0;
        c[_c].pt_sz = 0;
        c[_c].ps.resize(1100);
        c[_c].pt.resize(1100);
        memset(&c[_c].ps[0],0,1100*sizeof(Node));
        memset(&c[_c].pt[0],0,1100*sizeof(Node));

    }

    /*
    int pts_s[1100]; // short for potential sum of a student.
    // potential sum of a student i: sum of all student and teacher
    that student i can connect with (connect with = in the same council)
    int pts_t[1100]; // short for potential sum of a teacher.
    // potential sum of a teacher _t: sum of all student
    that teacher _t can connect with.
    */
    for(int i=1;i<=g.nStu;i++)
    {
        for(int j=1;j<=g.nStu;j++)
        {
            if(g.prj[i][j]>=g.minMatchStu&&g.prj[j][i]>=g.minMatchStu)
                pts_s[i] += g.prj[i][j] * BSF;
        }
        for (int _t=1;_t<=g.nProf;_t++)
        {
            if(g.prf[_t][i]>=g.minMatchProf)
            {
                pts_s[i] += g.prf[_t][i];
                pts_t[_t] += g.prf[_t][i];
            }
        }
    }
    //end set up data

    for(int _c=1;_c<=g.nC;_c++)
    {
        // Now we are going to find first pair of student - teacher

        int bt = -1;
        /*
        bt (short for best teacher)
        */

        for(int _t=1;_t<=g.nProf;_t++) // Iterate all teacher
        {
            // if Teacher _t has been selected, ignore
            if(TeacherSelected[_t]==(ll)(1)) continue;

            /*
            Iterate all teacher _t that satisfy:
            the number of student that teacher _t can NOW connect greater or equal
            than the minimun of number of students in a council.
            */
            if (t[_t].ssz>= g.minStu)
            {
                if( MethodFlag == 0  || MethodFlag == 2)
                {
                    /*
                    Among that teacher, we choose teacher with greatest potentail sum (pts_t[])
                    If many has equal greatest potentail sum,
                    choose teacher with greatest potential connection among them
                    (purpose: greatest potential connection can bring more member to that council)
                    */
                    if(bt==-1) // if no teacher was choosen -> choose that teacher
                    {
                        bt = _t;
                    }
                    else if(pts_t[_t]==pts_t[bt])  // if equally potential sum
                    {
                        if(t[_t].ssz>t[bt].ssz) // if greater connection -> update
                            bt = _t;
                    }
                    else if(pts_t[_t]>pts_t[bt]) // if greater potential sum -> update
                    {
                        bt = _t;
                    }
                }
                else if (MethodFlag==1 || MethodFlag == 3)
                {
                    /*
                    Among that teacher, we choose teacher with greatest potential connection (t[].ssz)
                    If many has equal greatest potential connection,
                    choose teacher with greatest potentail sum among them
                    */
                   if (t[_t].ssz>= g.minStu)
                    {
                        if(bt==-1) // if no teacher was choosen -> choose that teacher
                        {
                            bt = _t;
                        }
                        else if(t[_t].ssz==t[bt].ssz) // if equally potential connection
                        {
                            if(pts_t[_t]>pts_t[bt]) // if greater potential sum -> update
                                bt = _t;
                        }
                        else if(t[_t].ssz>t[bt].ssz) // if greater potential connection -> update
                        {
                            bt = _t;
                        }
                    }
                }
            }
        }
        if (bt == -1) // if can not choose any teacher -> no solution
        {
            return 0;
        }

        TeacherSelected[bt] = 1; // mark this teacher bt was selected
        c[_c].t.push_back(bt); // add this teacher into council _c

        // remove this teacher from all of the student potential sum
        for(int i = 1; i<=g.nStu;i++)
        {
            if (g.prf[bt][i]>=g.minMatchProf)
                pts_s[i] -= g.prf[bt][i];
        }
        //

        /*
        Now, we have our first teacher in this council (council _c).
        -> The set of students that can be placed in this council is a subset
        of the set of students that teacher bt can connect.
        */
        vector<int> StudentList;
        int now = 0;
        while(t[bt].s[now].next!=1004&&t[bt].s[now].next!=0)
        {
            now = t[bt].s[now].next;
            if(StudentSelected[now]==0)
                StudentList.push_back(now);
        }

        // set up ps: students that council _c can connect
        ps.clear();
        ps.resize(1100);
        memset(&ps[0],0,1100*sizeof(Node));
        ps_sz = ins(ps,StudentList);
        StudentList.clear();
        //end set up ps

        int bs = -1;
        /*
        bs (short for best student)
        */
        now = 0;
        // Iterate all student in ps
        while(ps[now].next!=1004&&ps[now].next!=0)
        {
            int _s = ps[now].next;
            // if student _s has been selected, ignore
            if(StudentSelected[_s]==1) continue;

            /*
            Iterate all student _s that satisfy:
            +) The number of student that student _s can NOW connect greater or equal
            than the minimun of number of students in a council minus 1 (himself/herself).
            +) The number of teacher that student _s can NOW connect greater or equal
            than the minimun of number of teachers in a council.
            */
            if(s[_s].tsz>=g.minProf&&s[_s].ssz>=g.minStu-1)
            {
                if (MethodFlag == 0 || MethodFlag == 2)
                {
                    /*
                    Among that student, we choose student with highest potentail sum: pts_s()
                    If many has equal highest potentail sum,
                    choose student with highest potential connection among them
                    (i.e. s[_s].tsz+s[_s].ssz)
                    (purpose: highest potential connection can bring more member to that council)
                    */
                    if(bs==-1) // if no student was choosen -> choose that teacher
                    {
                        bs = _s;
                    }
                    else if(pts_s[_s]==pts_s[bs]) // if equally potential sum
                    {
                        if(s[_s].tsz+s[_s].ssz>s[bs].tsz+s[bs].ssz) // if greater connection -> update
                        {
                            bs = _s;
                        }
                    }
                    else if(pts_s[_s]>pts_s[bs]) // if greater potential sum -> update
                    {
                        bs = _s;
                    }
                }
                else if (MethodFlag == 1 || MethodFlag == 3)
                {
                    /*
                    Among that student, we choose student with highest potentail connection, i.e. maximize(s[_s].tsz+s[_s].ssz)
                    If many has equal highest potentail connection,
                    choose student with highest potential sum among them
                    (i.e. pts_s())
                    */
                    if(s[_s].tsz>=g.minProf&&s[_s].ssz>=g.minStu-1)
                    {
                        if(bs==-1) // if no student was choosen -> choose that teacher
                        {
                            bs = _s;
                        }
                        else if(s[_s].tsz+s[_s].ssz==s[bs].tsz+s[bs].ssz) // if equally connection
                        {
                            if(pts_s[_s]>pts_s[bs]) // if greater potential sum -> update
                            {
                                bs = _s;
                            }
                        }
                        else if(s[_s].tsz+s[_s].ssz>s[bs].tsz+s[bs].ssz) // if greater connection -> update
                        {
                            bs = _s;
                        }
                    }
                }
            }
            // update next student in potential student double linked list
            now = ps[now].next;
        }
        if(bs==-1)
        {
            return 0;
        }

        StudentSelected[bs] = 1; // mark this student bs was selected
        c[_c].s.push_back(bs); // add this student into council _c

        // remove that student in all of the student potential sum
        for(int i = 1; i<=g.nStu;i++)
        {
            if(g.prj[i][bs]>=g.minMatchStu)//&&g.prj[bs][i]>=g.minMatchStu)
                pts_s[i] -= g.prj[i][bs] * BSF;
        }
        // remove that student in all of the teacher potential sum
        for(int _t = 1; _t<=g.nProf;_t++)
        {
            if(g.prf[_t][bs]>=g.minMatchProf)
                pts_t[_t] -= g.prf[_t][bs];
        }
        //
        /*
        Now, we have our first student in this council (council _c)
        -> The set of teachers that can be placed in this council is
        the set of teachers that student bs can connect.
        */
        vector<int> TeacherList;
        TeacherList.clear();
        now = 0;
        while(s[bs].t[now].next!=1004&&s[bs].t[now].next!=0)
        {
            now = s[bs].t[now].next;
            if(TeacherSelected[now]==0)
                TeacherList.push_back(now);
        }

        //set up pt: teacher thats council _c can connect
        pt.clear();
        pt.resize(1100);
        memset(&pt[0],0,1100*sizeof(Node));
        pt_sz = ins(pt,TeacherList);
        TeacherList.clear();
        //end set up pt

        // remove bs out of ps (bs was choosen -> bs is no more potential)
        ps_sz -= del(ps,bs);
        // remove bt out of ps (bt was choosen -> bt is no more potential)
        pt_sz -= del(pt,bt);

        /*
        Remove bs out of all:
        +) s[i].s (List of potential student that can be in same council with teacher _t)
        +) t[_t].s (List of potential student that can be in same council with teacher _t)
        Remove bt out of all:
        +) s[i].t (List of potential teacher that can be in same council with student i)
        */
        for(int i=1;i<=g.nStu;i++)
        {
            s[i].ssz-=del(s[i].s,bs);
            s[i].tsz-=del(s[i].t,bt);
        }
        for(int _t=1;_t<=g.nProf;_t++)
        {
            t[_t].ssz-=del(t[_t].s,bs);
        }

        // ps_sis[i]: number of student in both ps and s[i].s
        // pt_sit[i]: number of teacher in both ps and s[i].t
        for(int i=1;i<=g.nStu;i++)
        {
            if(ps_sz<s[i].ssz)
                ps_sis[i] = intersection(ps,s[i].s);
            else
                ps_sis[i] = intersection(s[i].s,ps);

            if(pt_sz<s[i].tsz)
                pt_sit[i] = intersection(pt,s[i].t);
            else
                pt_sit[i] = intersection(s[i].t,pt);
        }

        // pt_tts[_t]: number of teacher in both pt and t[_t].s
        for(int _t=1;_t<=g.nProf;_t++)
        {
            if(ps_sz<t[_t].ssz)
                ps_tts[_t] = intersection(ps,t[_t].s);
            else
                ps_tts[_t] = intersection(t[_t].s,ps);
        }

        bool StudentChecked[1100],TeacherChecked[1100];
        // StudentChecked[i] = 1 means that student i was iterated.
        // TeacherChecked[t] = 1 means that teacher i was iterated.
        memset(StudentChecked,0,1100*sizeof(bool));
        memset(TeacherChecked,0,1100*sizeof(bool));

        /*
        In this while loop, we will choose a student then a teacher, respectively until
        the number of teacher in this council = minProf
        and the number of student in this council = minStu
        */
        while (1)
        {
            int action = 0; // number of actions was done in each loop
            int cs_size = c[_c].s.size(); // number of students in this council NOW
            int ct_size = c[_c].t.size(); // number of teachers in this council NOW

            int bs = -1;
            /*
            bs (short for best student)
            */
            if (cs_size < g.minStu) // if not enough minimun student in this council
            {
                action++;
                int now = 0;
                //Iterate all student in ps
                while(ps[now].next!=1004&&ps[now].next!=0)
                {
                    int i = ps[now].next;
                    now = ps[now].next;
                    /*
                    There are 2 cases that make StudentChecked[i] = 1:
                    +) Student i was choosen to this council -> No more need to iterate this student
                    +) Student i was not match in this council -> No more need to iterate this student
                    */
                    if(StudentChecked[i]==1) continue;

                    // If student i was choosen before, ignore
                    if(StudentSelected[i]==1) continue;

                    // Begin check if this student can not match with anyone in this council
                    int check = 1;

                    for(auto _t: c[_c].t)
                    {
                        if(g.prf[_t][i]<g.minMatchProf) // This student was not match
                        {
                            check = 0;
                            break;
                        }
                    }
                    for(auto j: c[_c].s)
                    {
                        if(g.prj[i][j]<g.minMatchStu||g.prj[j][i]<g.minMatchStu)
                        // Student i was not match
                        {
                            check = 0;
                            break;
                        }
                    }
                    if(check==0)
                    {
                        StudentChecked[i] = 1;
                        continue;
                    }
                    // End check

                    // If we add this student, the maximum student and teacher for this council
                    // must be >= minStu and >= minProf, respectively.
                    if(ps_sis[i] + cs_size + 1 < g.minStu)
                        continue;
                    if(pt_sit[i] + ct_size < g.minProf)
                        continue;
                    if (MethodFlag == 0 || MethodFlag == 2)
                    {
                        // we will choose student with the greatest potential sum
                        if(bs==-1)
                        {
                            bs = i;
                        }
                        else if(pts_s[i]==pts_s[bs])
                        {
                            if(ps_sis[i]+pt_sit[i]>ps_sis[bs]+pt_sit[bs])
                            {
                                bs = i;
                            }
                        }
                        else if(pts_s[i]>pts_s[bs])
                        {
                            bs = i;
                        }
                    }
                    else if (MethodFlag == 1 || MethodFlag == 3)
                    {
                        // we will choose student with the greatest potential connection
                        if(bs==-1)
                        {
                            bs = i;
                        }
                        else if(ps_sis[i]+pt_sit[i]==ps_sis[bs]+pt_sit[bs])
                        {
                            if(pts_s[i]>pts_s[bs])
                            {
                                bs = i;
                            }
                        }
                        else if(ps_sis[i]+pt_sit[i]>ps_sis[bs]+pt_sit[bs])
                        {
                            bs = i;
                        }
                    }
                }
                if (bs==-1) // if can not choose any student -> no solution
                    return 0;

                c[_c].s.push_back(bs); // add this student into council _c

                // remove this student from all of the student potential sum
                for(int i = 1; i<=g.nStu;i++)
                {
                    if(g.prj[i][bs]>=g.minMatchStu)//&&g.prj[bs][i]>=g.minMatchStu)
                        pts_s[i] -= g.prj[i][bs] * BSF;
                }
                // remove this student from all of the teacher potential sum
                for(int _t = 1; _t<=g.nProf;_t++)
                {
                    if(g.prf[_t][bs]>=g.minMatchProf)
                        pts_t[_t] -= g.prf[_t][bs];
                }
                //

                // remove this student out of all potential list
                del(ps,bs);
                ps_sz--;
                for(int i=1;i<=g.nStu;i++)
                {
                    if(del(s[i].s,bs)==1)
                    {
                        ps_sis[i] -= 1;
                        s[i].ssz -=1;
                    }
                }
                for(int _t=1;_t<=g.nProf;_t++)
                {
                    if(del(t[_t].s,bs)==1)
                    {
                        t[_t].ssz -= 1;
                        ps_tts[_t] -= 1;
                    }
                }
                s[bs].s.clear();
                s[bs].t.clear();
                //

                StudentSelected[bs] = 1;
            }

            int bt = -1;
            /*
            bt (short for best teacher)
            */

            if( ct_size < g.minProf) // if not enough minimun teacher in this council
            {
                action++;
                cs_size = c[_c].s.size();
                int now = 0;
                //Iterate all teacher in pt
                while(pt[now].next!=1004&&pt[now].next!=0)
                {
                    int _t = pt[now].next;
                    now = pt[now].next;
                    /*
                    There are 2 cases that make TeacherChecked[_t] = 1:
                    +) Teacher _t was choosen to this council -> No more need to iterate this teacher
                    +) Teacher _t was not match in this council -> No more need to iterate this teacher
                    */
                    if(TeacherChecked[_t]==1) continue;

                    // If teacher _t was choosen before, ignore
                    if(TeacherSelected[_t]==1) continue;

                    // Begin check if this teacher can not match with anyone in this council
                    int check = 1;
                    for (auto i: c[_c].s)
                    {
                        if(g.prf[_t][i]<g.minMatchProf)
                        // This teacher is not match
                        {
                            check = 0;
                            break;
                        }
                    }
                    if(check==0)
                    {
                        TeacherChecked[_t] = 1;
                        continue;
                    }
                    // End check

                    // If we add this teacher, the maximum student for this council
                    // must be >= minStu respectively.
                    if(ps_tts[_t] + cs_size <g.minStu)
                        continue;
                        
                    if (MethodFlag == 0 || MethodFlag == 2)
                    {
                        // we will choose teacher with the greatest potential sum
                        if(bt==-1)
                        {
                            bt = _t;
                        }
                        else if (pts_t[_t]==pts_t[bt])
                        {
                            if (ps_tts[_t]>ps_tts[bt])
                            {
                                bt = _t;
                            }
                        }
                        else if (pts_t[_t]>pts_t[bt])
                        {
                            bt = _t;
                        }
                    }
                    else if (MethodFlag ==1 || MethodFlag == 3)
                    {
                        // we will choose teacher with the greatest potential connection
                        if(bt==-1)
                        {
                            bt = _t;
                        }
                        else if (ps_tts[_t]==ps_tts[bt])
                        {
                            if (pts_t[_t]>pts_t[bt])
                            {
                                bt = _t;
                            }
                        }
                        else if (ps_tts[_t]>ps_tts[bt])
                        {
                            bt = _t;
                        }
                    }
                    //
                }

                if(bt==-1) // if can not choose any teacher -> no solution
                    return 0;
                c[_c].t.push_back(bt); // add this teacher into council _c

                // remove this teacher from all of the student potential sum
                for(int i = 1; i<=g.nStu;i++)
                {
                    if(g.prf[bt][i]>=g.minMatchProf)
                        pts_s[i] -= g.prf[bt][i];
                }
                //*/

                // remove this teacher out of all potential list
                del(pt,bt);
                pt_sz--;
                for(int i=1;i<=g.nStu;i++)
                {
                    if(del(s[i].t,bt)==1)
                    {
                        pt_sit[i] -= 1;
                        s[i].tsz -= 1;
                    }
                }
                t[bt].s.clear();
                //

                TeacherSelected[bt] = 1;
            }
            if (action==0) // if no teacher and student was choosen in this loop -> end loop
            // -> number of student in this council NOW = minStu
            // -> number of teacher in this council NOW = minProf
                break;
        }

        // save remain ps and pt of council _c to c[_c].ps and c[_c].pt
        now = 0;
        StudentList.clear();
        while(ps[now].next!=1004&&ps[now].next!=0)
        {
            now = ps[now].next;
            StudentList.push_back(now);
        }
        c[_c].ps_sz = ins(c[_c].ps,StudentList);
        TeacherList.clear();
        now = 0;
        while(pt[now].next!=1004&&pt[now].next!=0)
        {
            now = pt[now].next;
            TeacherList.push_back(now);
        }
        c[_c].pt_sz = ins(c[_c].pt,TeacherList);
        TeacherList.clear();
    }

    // delete all selected student from all council potential student
    for(int i=1;i<=g.nStu;i++)
    {
        if(StudentSelected[i]==1)
        {
            for(int _c=1;_c<=g.nC;_c++)
            {
                c[_c].ps_sz -= del(c[_c].ps,i);
            }
        }
    }

    // delete all selected teacher from all council potential teacher
    for(int _t = 1; _t <= g.nProf ; _t++)
    {
        if(TeacherSelected[_t]==1)
        {
            for(int _c=1;_c<=g.nC;_c++)
            {
                c[_c].pt_sz -= del(c[_c].pt,_t);
            }
        }
    }
    //

    // sum_cs[_c][i] = The total match point of student i to council _c NOW
    // sum_ct[_c][_t] = The total match point of student _t to council _c NOW
    for(int _c=1;_c<=g.nC;_c++)
    {
        for(int i=1;i<=g.nStu;i++)
        {
            for (auto j: c[_c].s)
            {
                sum_cs[_c][i] += g.prj[i][j] * BSF;
            }
            for (auto _t: c[_c].t)
            {
                sum_cs[_c][i] += g.prf[_t][i];
            }
        }
        for(int _t = 1;_t<=g.nProf;_t++)
        {
            for (auto i: c[_c].s)
            {
                sum_ct[_c][_t] += g.prf[_t][i];
            }
        }
    }
    //*/

    int nit[1100],nis[1100];

    // Assign all remain teachers into councils
    for(int _t = 1; _t <= g.nProf ; _t++)
    {
        if(TeacherSelected[_t]==0)
        {
            int bc = -1;    // short for best council

            /*
            Now we will find the best council bc for teacher _t
            MethodFlag = 0,2:
                The idea is place that teacher into a council that match he/she best
                i.e. greatest sum_ct[bc][_t] = max(sum_ct[][_t])
            MethodFlag = 1,3:
                The idea is place that teacher into a council that can create
                a maximum potential connection for that council than put him/her in others.
                i.e. greatest nis[bc] = max(nis[])
            */
            for(int _c=1;_c<=g.nC;_c++)
            {
                // If that council is full of teachers, ignore
                if(c[_c].t.size()==g.maxProf) continue;
                // Check if this teacher can not match with anyone in this council
                int check = 1;
                for(auto j: c[_c].s)
                {
                    if(g.prf[_t][j]<g.minMatchProf)
                    {
                        check = 0;
                        break;
                    }
                }
                if (check==0) continue;

                /*
                nis[_c] (short for number of intersection of student):
                number of student in both
                c[_c].ps: potential student of council _c
                t[_t].s: potential student of teacher _t
                */
                nis[_c] = intersection(c[_c].ps,t[_t].s);
                if (MethodFlag == 0)
                {
                    if(bc==-1) // if no teacher was choosen -> choose that teacher
                    {
                        bc=_c;
                    }
                    else if(sum_ct[_c][_t]==sum_ct[bc][_t]) // if equally match
                    {
                        // if greater number of intersection of student -> update
                        if(nis[_c]>nis[bc])
                        {
                            bc = _c;
                        }
                    }
                    else if(sum_ct[_c][_t]>sum_ct[bc][_t]) // if greater match -> update
                    {
                        bc = _c;
                    }
                }
                else if (MethodFlag == 1)
                {
                    if(bc==-1)
                    {
                        bc=_c;
                    }
                    else if(nis[_c]==nis[bc])
                    {
                        if(sum_ct[_c][_t]>sum_ct[bc][_t])
                        {
                            bc = _c;
                        }
                    }
                    else if(nis[_c]>nis[bc])
                    {
                        bc = _c;
                    }
                }
                else if (MethodFlag == 2)
                {
                    if(bc==-1) // if no teacher was choosen -> choose that teacher
                    {
                        bc=_c;
                    }
                    else if(sum_ct[_c][_t]==sum_ct[bc][_t]) // if equally match
                    {
                        // nit[] is an array in the stack
                        // Basically, this is random swap
                        if(nit[_c]<nit[bc])
                        {
                            bc = _c;
                        }
                    }
                    else if(sum_ct[_c][_t]>sum_ct[bc][_t]) // if greater match -> update
                    {
                        bc = _c;
                    }
                }
                else if (MethodFlag == 3)
                {
                    if(bc==-1)
                    {
                        bc=_c;
                    }
                    else if(nis[_c]==nis[bc])
                    {
                        if(sum_ct[_c][_t]>sum_ct[bc][_t])
                        {
                            bc = _c;
                        }
                    }
                    else if(nis[_c]<nis[bc])
                    {
                        bc = _c;
                    }
                }
            }

            if(bc==-1) // if no council can be choosen -> No solution
            {
                return 0;
            }

            c[bc].t.push_back(_t); // add teacher _t into council bc

            // update total match of all students to council bc
            for(int i = 1;i<=g.nStu;i++)
            {
                sum_cs[bc][i] += g.prf[_t][i];
            }
            //

            // remove _t out of potential teacher list in all councils
            for(int _c=1;_c<=g.nC;_c++)
            {
                c[_c].pt_sz -= del(c[_c].pt,_t);
            }
            TeacherSelected[_t] = 1; // mark teacher _t as selected
        }
    }

    // Assign all remain students into councils
    for(int i=1;i<=g.nStu;i++)
    {
        if(StudentSelected[i]==0)
        {
            int bc = -1; // short for best council

            /*
            Now we will find the best council bc for student i
            Method 0,2:
                The idea is place that student into a council that match he/she best
                i.e. greatest sum_cs[bc][_t] = max(sum_cs[][_t])
            Method 1,3:
                The idea is place that student into a council that can create
                a maximum potential connection for that council than put him/her in another.
                i.e. greatest nis[bc]+nit[bc] = max(nis[]+nit[])
            */
            for(int _c=1;_c<=g.nC;_c++)
            {
                // If that council is full of students, ignore
                if(c[_c].s.size()==g.maxStu) continue;

                // Check if this student can not match with anyone in this council
                int check = 1;
                for(auto j: c[_c].s)
                {
                    if(g.prj[i][j]<g.minMatchStu||g.prj[j][i]<g.minMatchStu)
                    {
                        check = 0;
                        break;
                    }
                }
                for(auto _t: c[_c].t)
                {
                    if(g.prf[_t][i]<g.minMatchProf)
                    {
                        check = 0;
                        break;
                    }
                }
                if(check==0) continue;

                /*
                nis[_c] (short for number of intersection of student):
                number of student in both
                c[_c].ps: potential student list of council _c
                s[i].s: potential student list of student i
                */
                nis[_c] = intersection(c[_c].ps,s[i].s);

                /*
                nit[_c] (short for number of intersection of teacher):
                number of teacher in both
                c[_c].pt: potential teacher list of council _c
                s[i].t: potential teacher list of student i
                */
                nit[_c] = intersection(c[_c].pt,s[i].t);

                if (MethodFlag == 0)
                {
                    if(bc==-1) // if no student was choosen -> choose that student
                    {
                        bc = _c;
                    }
                    else if(sum_cs[_c][i]==sum_cs[bc][i]) // if equally match
                    {
                        // if greater number of intersection of student and teacher -> update
                        if (nis[_c]+nit[_c]<nis[bc]+nit[bc])
                        {
                            bc = _c;
                        }
                    }
                    else if(sum_cs[_c][i]>sum_cs[bc][i]) // if greater match -> update
                    {
                        bc = _c;
                    }
                }
                else if (MethodFlag == 1)
                {
                    if(bc==-1)
                    {
                        bc = _c;
                    }
                    else if (nis[_c]+nit[_c]==nis[bc]+nit[bc])
                    {
                        if(sum_cs[_c][i]>sum_cs[bc][i])
                        {
                            bc = _c;
                        }
                    }
                    else if (nis[_c]+nit[_c]>nis[bc]+nit[bc])
                    {
                        bc = _c;
                    }
                }
                else if (MethodFlag == 2)
                {
                    if(bc==-1) // if no student was choosen -> choose that student
                    {
                        bc = _c;
                    }
                    else if(sum_cs[_c][i]==sum_cs[bc][i]) // if equally match
                    {
                        // if less number of intersection of student and teacher -> update
                        if (nis[_c]+nit[_c]<nis[bc]+nit[bc])
                        {
                            bc = _c;
                        }
                    }
                    else if(sum_cs[_c][i]>sum_cs[bc][i]) // if greater match -> update
                    {
                        bc = _c;
                    }
                }
                else if (MethodFlag == 3)
                {
                    if(bc==-1)
                    {
                        bc = _c;
                    }
                    else if (nis[_c]+nit[_c]==nis[bc]+nit[bc])
                    {
                        if(sum_cs[_c][i]>sum_cs[bc][i])
                        {
                            bc = _c;
                        }
                    }
                    else if (nis[_c]+nit[_c]<nis[bc]+nit[bc])
                    {
                        bc = _c;
                    }
                }
            }

            if(bc==-1) // if no council can be choosen -> No solution
            {
                return 0;
            }

            c[bc].s.push_back(i); // add student i into council _t

            // update total match of all students to council bc
            for(int j = 1;j<=g.nStu;j++)
            {
                sum_cs[bc][j] += g.prj[i][j] * BSF;
            }
            // update total match of all students to council bc
            for(int _t = 1; _t<=g.nProf;_t++)
            {
                sum_ct[bc][_t] += g.prf[_t][i];
            }
            //

            // remove i out of potential student list in all councils
            for(int _c=1;_c<=g.nC;_c++)
            {
                c[_c].ps_sz -= del(c[_c].ps,i);
            }
            StudentSelected[i] = 1;
        }
    }

    return 1;
}

int TeacherAns[1100], StudentAns[1100];

clock_t BeginTime;

int MaxAns = 0, _ans;

// Check if we can place StudentToCheck into council _c
bool CheckStudentToCouncil(int _c,int StudentToCheck, int StudentToSwap)
{
    for(auto i: c[_c].s)
    {
        if (i!=StudentToSwap)
        {
            if (g.prj[StudentToCheck][i] < g.minMatchStu || g.prj[i][StudentToCheck] < g.minMatchStu)
                return false;
        }
    }
    for(auto _t: c[_c].t)
    {
        if (g.prf[_t][StudentToCheck] < g.minMatchProf)
            return false;
    }
    return true;
}

// Get total match point of a student to a council
int GetSumStudentCouncil(int _c,int TargetStudent)
{
    int Ans1 = 0;
    for (auto j: c[_c].s)
    {
        Ans1 += g.prj[TargetStudent][j]; //+ g.prj[j][TargetStudent];
    }
    for (auto _t: c[_c].t)
    {
        Ans1 += g.prf[_t][TargetStudent];
    }
    return Ans1;
}

bool CheckSumSwapStudent(int StudentA, int StudentB)
{
    // find place of StudentA and StudentB in his/her councils
    int idA = 0;
    int _cA = StudentAns[StudentA];
    for(int i = 0;i<c[_cA].s.size();i++)
    {
        if (c[_cA].s[i]==StudentA)
        {
            idA = i;
            break;
        }
    }
    int idB = 0;
    int _cB = StudentAns[StudentB];
    for (int i=0;i<c[_cB].s.size();i++)
    {
        if (c[_cB].s[i]==StudentB)
        {
            idB = i;
            break;
        }
    }

    //Calculate old sum
    int OldSum = GetSumStudentCouncil(_cA,StudentA) + GetSumStudentCouncil(_cB,StudentB);

    // Swap StudentA ans StudentB
    swap(c[_cA].s[idA], c[_cB].s[idB]);
    swap(StudentAns[StudentA],StudentAns[StudentB]);
    //Calculate new sum
    int NewSum = GetSumStudentCouncil(_cA,StudentB) + GetSumStudentCouncil(_cB,StudentA);

    if (OldSum>=NewSum) // if NewSum less than OldSum, swap back
    {
        swap(StudentAns[StudentA],StudentAns[StudentB]);
        swap(c[_cA].s[idA], c[_cB].s[idB]);
        return false;
    }
    else
        return true;
}

int GetRunTime(int StartTime)
{
    return double(clock()-StartTime)/double(CLOCKS_PER_SEC);
}

bool CheckTeacherToCouncil(int _c,int TargetTeacher)
{
    for(auto i: c[_c].s)
    {
        if (g.prf[TargetTeacher][i] < g.minMatchProf)
            return false;
    }
    return true;
}

int GetSumTeacherCouncil(int _c, int TargetTeacher)
{
    int Ans1 = 0;
    for (auto i: c[_c].s)
    {
        Ans1 += g.prf[TargetTeacher][i];
    }
    return Ans1;
}

bool CheckSumSwapTeacher(int TeacherA, int TeacherB)
{
    // find place of StudentA and StudentB in his/her councils
    int idA = 0;
    int _cA = TeacherAns[TeacherA];
    for(int _t = 0;_t < c[_cA].t.size();_t++)
    {
        if (c[_cA].t[_t]==TeacherA)
        {
            idA = _t;
            break;
        }
    }
    int idB = 0;
    int _cB = TeacherAns[TeacherB];
    for (int _t=0;_t < c[_cB].t.size();_t++)
    {
        if (c[_cB].t[_t]==TeacherB)
        {
            idB = _t;
            break;
        }
    }

    //Calculate old sum
    int OldSum = GetSumTeacherCouncil(_cA,TeacherA) + GetSumTeacherCouncil(_cB,TeacherB);

    // Swap TeacherA ans TeacherB
    swap(c[_cA].t[idA], c[_cB].t[idB]);
    swap(TeacherAns[TeacherA],TeacherAns[TeacherB]);
    //Calculate new sum
    int NewSum = GetSumTeacherCouncil(_cA,TeacherB) + GetSumTeacherCouncil(_cB,TeacherA);

    if (OldSum>=NewSum) // if NewSum less than OldSum, swap back
    {
        swap(TeacherAns[TeacherA],TeacherAns[TeacherB]);
        swap(c[_cA].t[idA], c[_cB].t[idB]);
        return false;
    }
    else
        return true;
}

double TimeLimit = double(20.0);

void HillClimbing()
{
    clock_t TimeNow = clock();
    while(GetRunTime(TimeNow)<TimeLimit)// Check if we are out of time
    {
        bool check = 0;
        for (int i=1;i<=g.nStu;i++)
        {
            for (int j=1;j<=g.nStu;j++)
            {
                // if they are not in the same council
                if (StudentAns[i]!=StudentAns[j])
                {
                    // check if both of them can swap council
                    if (CheckStudentToCouncil(StudentAns[i],j,i) == false || CheckStudentToCouncil(StudentAns[j],i,j) == false)
                        continue;
                    // Try to swap
                    if (CheckSumSwapStudent(i,j)) // So we swapped at least a pair of students. 
                    {
                        check = 1;
                        break;
                    }
                    // Check if we are out of time
                    if(GetRunTime(TimeNow) > TimeLimit)
                        return;
                }
            }
        }
        if (check==1) continue; // if we swapped at least a pair of students before, continue to try to swap student. If we could not swap any student, try to swap teacher.
        check = 0;
        for (int t1=1;t1<=g.nProf;t1++)
        {
            for (int t2=1;t2<=g.nProf;t2++)
            {
                // if they are not in the same council
                if (TeacherAns[t1]!=TeacherAns[t2])
                {
                    // check if both of them can swap council
                    if (CheckTeacherToCouncil(TeacherAns[t1],t2) == false || CheckTeacherToCouncil(TeacherAns[t2],t1) == false)
                        continue;
                    //Try to swap
                    if (CheckSumSwapTeacher(t1,t2)) // So we swapped at least a pair of teachers.
                    {
                        check = 1;
                        break;
                    }
                }
                // Check if we are out of time
                if(GetRunTime(TimeNow) > TimeLimit )
                    return;
            }
        }
        if (check==0) return; // If we found a local optima, exit the hill climbing
    }
}

int Solve(int MethodFlag,int PrioritizeStudentsFlag)
{
    if (FindArbitrarySolution(MethodFlag, PrioritizeStudentsFlag) == 0)
    {
        return 0;
    }

    for(int _c=1;_c<=g.nC;_c++)
    {
        for(auto i: c[_c].s)
        {
            StudentAns[i] = _c;
        }
        for(auto _t: c[_c].t)
        {
            TeacherAns[_t] = _c;
        }
    }

    HillClimbing();
    int Ans = 0;
    for (int i = 1; i <= g.nStu; i++)
    {
        for (int j = i+1 ; j <= g.nStu; j++)
        {
            if (StudentAns[i]==StudentAns[j])
            {
                Ans += g.prj[i][j];
            }
        }
        for (int _t = 1; _t <= g.nProf ; _t++)
        {
            if (StudentAns[i]==TeacherAns[_t])
            {
                Ans += g.prf[_t][i];
            }
        }
    }
    return Ans;
}

int FinalTeacherAns[1100], FinalStudentAns[1100];



void input()
{
    BeginTime = clock();
    cin>>g.nStu>>g.nProf>>g.nC;
    cin>>g.minStu>>g.maxStu>>g.minProf>>g.maxProf>>g.minMatchStu>>g.minMatchProf;
    for(int i=1;i<=g.nStu;i++)
    {
        for(int j=1;j<=g.nStu;j++)
        {
            int gg;
            cin>>gg;
            if (i==j || gg<g.minMatchStu)
            {
                gg = 0;
            }
            g.prj[i][j] = gg;
        }
    }
    for (int i=1;i<=g.nStu;i++)
    {
        for(int _t=1;_t<=g.nProf;_t++)
        {
            int gg = 0;
            cin>>gg;
            if (gg<g.minMatchProf)
                gg = 0;
            g.prf[_t][i] = gg;
        }
    }
    for(int i=1;i<=g.nStu;i++)
    {
        int gg; cin>>gg;
        g.prf[gg][i] = 0;
    }

    for(int i=1;i<=g.nStu;i++)
    {
        for(int j=1;j<=g.nStu;j++)
        {
            if (g.prj[i][j]<g.minMatchStu)
            {
                g.prj[i][j] = 0;
                g.prj[j][i] = 0;
            }
        }
    }

    bool SolutionExist = 0;
    int MaxAnsForAll = 0;
    int BestMethod = 0;
    int BestPrioritizeStudentsFlag = 0;
    int AnsForMethod[4][3];
    for (int Method = 0; Method < 4; Method++)
    {
        // BSF: PrioritizeStudentsFlag
        for (int BSF = 1; BSF <= 2; BSF++)
        {
            AnsForMethod[Method][BSF] = Solve(Method,BSF);
            if(AnsForMethod[Method][BSF] > MaxAnsForAll)
            {
                BestMethod = Method;
                BestPrioritizeStudentsFlag = BSF;
                MaxAnsForAll = AnsForMethod[Method][BSF];
                for (int i = 1; i <= g.nStu ; i++)
                {
                    FinalStudentAns[i] = StudentAns[i];
                }
                for (int _t = 1; _t <= g.nProf; _t++)
                {
                    FinalTeacherAns[_t] = TeacherAns[_t];
                }
                SolutionExist = 1;
            }
        }
    }

    if (SolutionExist==0)
    {
        cout<<"No solution"<<el;
        exit(0);
    }

    cout<<g.nStu<<el;
    for (int i=1;i<=g.nStu;i++)
    {
        cout<<FinalStudentAns[i]<<" ";
    }
    cout<<el<<g.nProf<<el;
    for (int _t=1;_t<=g.nProf;_t++)
    {
        cout<<FinalTeacherAns[_t]<<" ";
    }

    cout<<el<<el<<"Answer is: "<<MaxAnsForAll<<el;
    cout<<"Best method is: Method "<<BestMethod*2 + BestPrioritizeStudentsFlag<<el;
    cout<<"Solve in "<<double(clock()-BeginTime)/double(CLOCKS_PER_SEC)<<"s."<<el<<el;

    cout<<"Answer for all methods: "<<el;
    for (int i=0;i<4;i++)
    {
        for (int j=1;j<=2;j++)
        {
            cout<<"Method "<<i*2+j<<": ";
            if (AnsForMethod[i][j]==0)
            {
                cout<<"No solution"<<el;
            }
            else cout<<AnsForMethod[i][j]<<el;
        }
    }
    cout<<el;

    cout<<"Councils distribution for method "<<BestMethod*2 + BestPrioritizeStudentsFlag<<":"<<el<<el;

    for(int _c=1;_c<=g.nC;_c++)
    {
        cout<<"Council "<<_c<<":"<<el;
        int TeacherCount = 0, StudentCount = 0;
        for (int i = 1; i <= g.nStu ; i++)
        {
            StudentCount += (FinalStudentAns[i] ==  _c);
        }
        for (int _t = 1; _t <= g.nProf; _t++)
        {
            TeacherCount += (FinalTeacherAns[_t] == _c);
        }
        cout<<StudentCount<<" project: "<<el;
        for (int i = 1; i <= g.nStu ; i++)
        {
            if (FinalStudentAns[i] ==  _c)
            {
                cout<<i<<" ";
            }
        }
        cout<<el;
        cout<<TeacherCount<<" teacher: "<<el;
        for (int _t = 1; _t <= g.nProf; _t++)
        {
            if (FinalTeacherAns[_t] == _c)
            {
                cout<<_t<<" ";
            }
        }
        cout<<el<<el;
    }
}

signed main()
{
    ios_base::sync_with_stdio(false);
    cin.tie(0);
    freopen("data.inp","r",stdin);
    freopen("HeuristicAns.out","w",stdout);
    int test = 1;
    //cin>>test;
    while(test--)
    {
        input();
    }
}
