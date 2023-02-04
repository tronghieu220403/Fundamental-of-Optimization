#include <bits/stdc++.h>

using namespace std;

#define el '\n'

#define int long long

typedef long long ll;

typedef unsigned long long ull;

typedef long double ld;

const int MaxN = 1e6+1e5;

const ll mod = 1e9+7;

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
    int miniStu, maxStu, miniProf, maxProf, minMatchStu, minMatchProf;
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

int solve(int e, int f)
{
    g.minMatchStu = e;
    g.minMatchProf = f;

    // set up data
    for(int i=1;i<=g.nStu;i++)
    {
        s[i].t.clear();
        s[i].t.resize(1100);
        s[i].s.clear();
        s[i].s.resize(1100);
        memset(&s[i].s[0],0,1100*sizeof(Node));
        memset(&s[i].t[0],0,1100*sizeof(Node));
    }
    for(int _t=1;_t<=g.nProf;_t++)
    {
        t[_t].s.clear();
        t[_t].s.resize(1100);
        memset(&t[_t].s[0],0,1100*sizeof(Node));
    }
    //end set up data

    /*
    Setting up double linked list for s[i].s, s[i].t, t[_t].s
    */
    vector<int> StudentList, TeacherList;
    for(int i=1;i<=g.nStu;i++)
    {
        for(int j=1;j<=g.nStu;j++)
        {
            // if student i and student j have a possibility to be in a same group
            if (g.prj[i][j]>=g.minMatchStu && g.prj[j][i]>=g.minMatchStu)
            {
                StudentList.push_back(j);
            }
        }
        // s[i].s: List of student that can be in same council with student i
        s[i].ssz = ins(s[i].s,StudentList);
        for (int _t=1;_t<=g.nProf;_t++)
        {
            // if student i and teacher t have a possibility to be in a same group
            if (g.prf[_t][i]>=g.minMatchProf)
            {
                TeacherList.push_back(_t);
            }
        }
        //s[i].t: List of teacher that can be in same council with student i
        s[i].tsz = ins(s[i].t,TeacherList);
        StudentList.clear();
        TeacherList.clear();
    }

    for (int _t=1;_t<=g.nProf;_t++)
    {
        for (int i=1;i<=g.nStu;i++)
        {
            // if student i and teacher t have a possibility to be in a same group
            if (g.prf[_t][i]>=g.minMatchProf)
            {
                StudentList.push_back(i);
            }
        }
        //t[_t].s: List of student that can be in same council with teacher _t
        t[_t].ssz = ins(t[_t].s,StudentList);
        StudentList.clear();
    }

    //set up data
    pt.clear();ps.clear();
    int lit[1100],lis[1100];
    int lit1[1100],lis1[1100];

    int StudentSelected[1100],TeacherSelected[1100];
    // StudentSelected[i] = 1 means that student i (project i) was selected
    // TeacherSelected[_t] = 1 means that teacher _t was selected
    fill(StudentSelected,StudentSelected+1050,0);
    fill(TeacherSelected,TeacherSelected+1050,0);
    int ps_sz; //potential student size
    int pt_sz; //potential teacher size
    
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
    }
    //end set up data

    for(int _c=1;_c<=g.nC;_c++)
    {
        // Now we are going to find first pair of student - teacher

        int mt = -1;    // mt (short for max teacher): teacher that have the most student that can be in the same council
        // Among all teacher, choose 
        for(int _t=1;_t<=g.nProf;_t++)
        {
            // if Teacher _t has been selected, ignore
            if(TeacherSelected[_t]==(ll)(1)) continue;

            /*
            Go through all teacher _t that satisfy:
            the number of student that teacher _t can NOW connect greater or equal
            than the minimun of number of students in a council.
            We choose teacher with highest potentail connection
            (purpose: highest potential connection can bring more member to that council)
            */
            if (t[_t].ssz>= g.miniStu)
            {
                if(mt==-1) // if no teacher was choosed -> choose that teacher
                    mt = _t;
                else if(t[_t].ssz>t[mt].ssz) // if higher potential connection -> update
                {
                    mt = _t;
                }
            }
        }
        if (mt == -1)
        {
            return 0;
        }
        if (mt == -1) // if can not choose any teacher -> no solution
        {
            return 0;
        }

        TeacherSelected[mt] = 1; // mark that teacher mt was selected
        c[_c].t.push_back(mt); // add that teacher to council _c

        vector<int> trash;
        int now = 0;
        while(t[mt].s[now].next!=1004&&t[mt].s[now].next!=0)
        {
            now = t[mt].s[now].next;
            if(StudentSelected[now]==0)
                trash.push_back(now);
        }
        ps.resize(1100);
        memset(&ps[0],0,1100*sizeof(Node));
        ps_sz = ins(ps,trash);
        trash.clear();
        int ms = -1;
        now = 0;
        while(ps[now].next!=1004&&ps[now].next!=0)
        {
            int _s = ps[now].next;
            now = ps[now].next;
            if(StudentSelected[_s]==1) continue;
            if(s[_s].tsz>=g.miniProf&&s[_s].ssz>=g.miniStu-1)
            {
                if(ms==-1)
                {
                    ms = _s;
                }
                else if(s[_s].tsz+s[_s].ssz>s[ms].tsz+s[ms].ssz)
                {
                    ms = _s;
                }
            }
        }
        if(ms==-1)
        {
            return 0;
        }
        StudentSelected[ms] = 1;
        c[_c].s.push_back(ms);

        trash.clear();
        now = 0;
        while(s[ms].t[now].next!=1004&&s[ms].t[now].next!=0)
        {
            now = s[ms].t[now].next;
            if(TeacherSelected[now]==0)
                trash.push_back(now);
        }
        
        pt.clear(); // 
        ps.clear(); //  
        pt.resize(1100);
        memset(&pt[0],0,1100*sizeof(Node));
        pt_sz = ins(pt,trash);
        trash.clear();
        del(ps,ms);
        ps_sz--;
        del(pt,mt);
        pt_sz--;
        for(int i=1;i<=g.nStu;i++)
        {
            s[i].ssz-=del(s[i].s,ms);
            s[i].tsz-=del(s[i].t,mt);
        }
        for(int _t=1;_t<=g.nProf;_t++)
        {
            t[_t].ssz-=del(t[_t].s,ms);
        }

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

        for(int _t=1;_t<=g.nProf;_t++)
        {
            if(ps_sz<t[_t].ssz)
                ps_tts[_t] = intersection(ps,t[_t].s);
            else
                ps_tts[_t] = intersection(t[_t].s,ps);
        }

        bool checks[1100],checkt[1100];
        memset(checks,0,1100*sizeof(bool));
        memset(checkt,0,1100*sizeof(bool));

        while (1)
        {
            int action = 0;
            int cs = c[_c].s.size();
            int ct = c[_c].t.size();
            int ms = -1;
            if ( cs >= g.miniStu )
                action = 1;
            else
            {
                int now = 0;
                while(ps[now].next!=1004&&ps[now].next!=0)
                {
                    int i = ps[now].next;
                    now = ps[now].next;
                    if(checks[i]==1) continue;
                    if(StudentSelected[i]==1) continue;

                    int check = 1;
                    for(auto _t: c[_c].t)
                    {
                        if(g.prf[_t][i]<g.minMatchProf)
                        {
                            check = 0;
                            break;
                        }
                    }
                    for(auto j: c[_c].s)
                    {
                        if(g.prj[i][j]<g.minMatchStu||g.prj[j][i]<g.minMatchStu)
                        {
                            check = 0;
                            break;
                        }
                    }
                    if(check==0)
                    {
                        checks[i] = 1;
                        continue;
                    }
                    lis[i] = ps_sis[i];
                    lit[i] = pt_sit[i];

                    if(lis[i] + cs + 1 < g.miniStu)
                        continue;
                    if(lit[i] + ct < g.miniProf)
                        continue;
                    if(ms==-1)
                    {
                        ms = i;
                    }
                    else if(lis[i]+lit[i]>lis[ms]+lit[ms])
                    {
                        ms = i;
                    }
                }

                if (ms==-1)
                    return 0;
                c[_c].s.push_back(ms);

                for(int i=1;i<=g.nStu;i++)
                {
                    if(del(s[i].s,ms)==1)
                    {
                        ps_sis[i] -= 1;
                        s[i].ssz -=1;
                    }
                }
                for(int _t=1;_t<=g.nProf;_t++)
                {
                    //t[_t].ssz -= del(t[_t].s,ms);
                    if(del(t[_t].s,ms)==1)
                    {
                        t[_t].ssz -= 1;
                        ps_tts[_t] -= 1;
                    }
                }

                del(ps,ms);
                ps_sz--;
                s[ms].s.clear();
                s[ms].t.clear();
                StudentSelected[ms] = 1;

            }
            int mt = -1;
            if( ct >= g.miniProf)
            {
                action++;
            }
            else
            {
                cs = c[_c].s.size();
                int now = 0;
                while(pt[now].next!=1004&&pt[now].next!=0)
                {
                    int _t = pt[now].next;
                    now = pt[now].next;
                    if(checkt[_t]==1) continue;
                    if(TeacherSelected[_t]==1) continue;

                    int check = 1;
                    for (auto i: c[_c].s)
                    {
                        if(g.prf[_t][i]<g.minMatchProf)
                        {
                            check = 0;
                            break;
                        }
                    }
                    if(check==0)
                    {
                        checkt[_t] = 1;
                        continue;
                    }

                    lis[_t] = ps_tts[_t];
                    if(lis[_t] + cs <g.miniStu)
                        continue;
                    if(mt==-1)
                    {
                        mt = _t;
                    }
                    else if (lis[_t]>lis[mt])
                    {
                        mt = _t;
                    }
                }
                if(mt==-1)
                    return 0;
                c[_c].t.push_back(mt);

                del(pt,mt);
                pt_sz--;
                for(int i=1;i<=g.nStu;i++)
                {
                    //s[i].tsz -= del(s[i].t,mt);
                    if(del(s[i].t,mt)==1)
                    {
                        pt_sit[i] -= 1;
                        s[i].tsz -= 1;
                    }
                }
                t[mt].s.clear();
                TeacherSelected[mt] = 1;
            }
            //cout<<"choose teacher and student: "<<mt<<" "<<ms<<el<<flush;
            if (action==2)
                break;
        }
        now = 0;
        trash.clear();
        while(ps[now].next!=1004&&ps[now].next!=0)
        {
            now = ps[now].next;
            trash.push_back(now);
        }
        c[_c].ps_sz = ins(c[_c].ps,trash);
        trash.clear();
        now = 0;
        while(pt[now].next!=1004&&pt[now].next!=0)
        {
            now = pt[now].next;
            trash.push_back(now);
        }
        c[_c].pt_sz = ins(c[_c].pt,trash);
        trash.clear();
    }

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


    for(int _t = 1; _t <= g.nProf ; _t++)
    {
        if(TeacherSelected[_t]==0)
        {
            int mc = -1;
            for(int _c=1;_c<=g.nC;_c++)
            {
                if(c[_c].t.size()==g.maxProf) continue;
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

                lis[_c] = intersection(c[_c].ps,t[_t].s);

                if(mc==-1)
                {
                    mc=_c;
                }
                else if(lit[_c]<lit[mc])
                {
                    mc = _c;
                }
            }
            if(mc==-1)
            {
                return 0;
            }

            c[mc].t.push_back(_t);

            for(int _c=1;_c<=g.nC;_c++)
            {
                c[_c].pt_sz -= del(c[_c].pt,_t);
            }
            TeacherSelected[_t] = 1;
        }
    }

    for(int i=1;i<=g.nStu;i++)
    {
        if(StudentSelected[i]==0)
        {
            int mc = -1;
            for(int _c=1;_c<=g.nC;_c++)
            {
                if(c[_c].s.size()==g.maxStu) continue;
                int check = 1;
                int dem =0;
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
                lis[_c] = intersection(c[_c].ps,s[i].s);
                lit[_c] = intersection(c[_c].pt,s[i].t);

                if(mc==-1)
                {
                    mc = _c;
                }
                else if (lis[_c]+lit[_c]<lis[mc]+lit[mc])
                {
                    mc = _c;
                }
            }
            if(mc==-1) return 0;

            c[mc].s.push_back(i);
            for(int _c=1;_c<=g.nC;_c++)
            {
                c[_c].ps_sz -= del(c[_c].ps,i);
            }
            StudentSelected[i] = 1;
        }
    }

    return 1;
}

void input()
{
    cin>>g.nStu>>g.nProf>>g.nC;
    cin>>g.miniStu>>g.maxStu>>g.miniProf>>g.maxProf>>g.minMatchStu>>g.minMatchProf;
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

    clock_t BeginTime = clock();
    if(solve(g.minMatchStu,g.minMatchProf)==0)
    {
        cout<<"No solution"<<el;
        exit(0);
    }

    int ans = 0;

    for(int _c=1;_c<=g.nC;_c++)
    {
        cout<<"Council "<<_c<<":"<<el;
        cout<<c[_c].s.size()<<" project: "<<el;
        for(auto i: c[_c].s)
        {
            cout<<i<<" ";
            for(auto j: c[_c].s)
            {
                if(i!=j)
                    ans += g.prj[i][j];
            }
        }
        cout<<el;
        cout<<c[_c].t.size()<<" teacher: "<<el;
        for(auto _t: c[_c].t)
        {
            cout<<_t<<" ";
            for(auto i: c[_c].s)
            {
                ans += g.prf[_t][i];
            }
        }
        cout<<el<<el;
    }
    cout<<el<<el<<"Answer is: "<<ans<<el;
    cout<<"Solve in "<<double(clock()-BeginTime)/double(CLOCKS_PER_SEC)<<"s.";
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
