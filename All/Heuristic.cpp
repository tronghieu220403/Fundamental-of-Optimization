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

int guide[10000];

struct dou_ll
{
    int prev;
    int next;
};

int del(vector<dou_ll> &a, int id)
{
    //if(a[id].prev==0&&a[id].next==1004)
        //return 0;
    if(a[id].prev==0&&a[id].next<=id)
        return 0;
    a[a[id].prev].next = a[id].next;
    a[a[id].next].prev = a[id].prev;
    a[id].next = 0;
    a[id].prev = 0;
    return 1;
}

int ins(vector<dou_ll> &target, vector<int> &source)
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
    vector<dou_ll> ps;
    vector<dou_ll> pt;
    int ps_sz;
    int pt_sz;
};

Council c[1104];

struct info
{
    int nStu,nProf,nC;
    int miniStu, maxStu, miniProf, maxProf, minMatchStu, minMachProf;
    int prj[1104][1104], prf[1104][1104];
    int g[1104];
};

info g;

struct linked
{
    vector<dou_ll> s;
    vector<dou_ll> t;
    int ssz,tsz;
};

linked t[1104],s[1104];

clock_t TotalTime = 0;

int intersection(vector<dou_ll> &p,vector<dou_ll> &pa)
{
    clock_t t0 = clock();
    int ans = 0;
    int now1 = 0;
    while(p[now1].next!=1004&&p[now1].next!=0)
    {
        int val = p[now1].next;
        if(pa[val].next!=0)
            ans++;
        now1 = p[now1].next;
    }
    TotalTime += clock()-t0;
    return ans;
}

vector<dou_ll> pt,ps,pta,psa;

int ps_sis[1100];
int pt_sit[1100];
int ps_tts[1100];

int solve(int e, int f)
{
    g.minMatchStu = e;
    g.minMachProf = f;

    //cout<<endl<<"e and f is: ";
    //cout<<e<<" "<<f<<el<<flush;

    for(int i=1;i<=g.nStu;i++)
    {
        s[i].t.clear();
        s[i].t.resize(1100);
        s[i].s.clear();
        s[i].s.resize(1100);
        memset(&s[i].s[0],0,1100*sizeof(dou_ll));
        memset(&s[i].t[0],0,1100*sizeof(dou_ll));
    }
    for(int _t=1;_t<=g.nProf;_t++)
    {
        t[_t].s.clear();
        t[_t].s.resize(1100);
        memset(&t[_t].s[0],0,1100*sizeof(dou_ll));
    }

    vector<int> trash,trash1;
    for(int i=1;i<=g.nStu;i++)
    {
        for(int j=1;j<=g.nStu;j++)
        {
            if (g.prj[i][j]>=g.minMatchStu && g.prj[j][i]>=g.minMatchStu)
            {
                //s[i].s.insert(j);
                trash.push_back(j);
            }
        }
        s[i].ssz = ins(s[i].s,trash);
        for (int _t=1;_t<=g.nProf;_t++)
        {
            if (g.prf[_t][i]>=g.minMachProf)
            {
                //s[i].t.insert(_t);
                trash1.push_back(_t);
            }
        }
        s[i].tsz = ins(s[i].t,trash1);
        trash1.clear();
        trash.clear();
    }
    //cout<<"OKE"<<flush;
    for (int _t=1;_t<=g.nProf;_t++)
    {
        for (int i=1;i<=g.nStu;i++)
        {
            if (g.prf[_t][i]>=g.minMachProf)
            {
                //t[_t].s.insert(i);
                trash.push_back(i);
            }
        }
        t[_t].ssz = ins(t[_t].s,trash);
        trash.clear();
    }
    pt.clear();ps.clear();psa.clear();pta.clear();
    int lit[1100],lis[1100];
    int lit1[1100],lis1[1100];

    int sels[1100],selt[1100];
    fill(sels,sels+1050,0);
    fill(selt,selt+1050,0);
    int ps_sz, pt_sz;
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

    for(int _c=1;_c<=g.nC;_c++)
    {
        pt.clear();
        ps.clear();
        int mt1 = -1;
        for(int _t=1;_t<=g.nProf;_t++)
        {
            if(selt[_t]==(ll)(1)) continue;
            if(guide[_t]==1)
            {
                mt1 = _t;
                break;
            }
            if (t[_t].ssz>= g.miniStu)
            {
                if(mt1==-1)
                    mt1 = _t;
                else
                {
                    if(t[_t].ssz>t[mt1].ssz)
                        mt1 = _t;
                }
            }
        }
        if (mt1 == -1)
        {
            return 0;
        }
        selt[mt1] = 1;
        c[_c].t.push_back(mt1);

        vector<int> trash;
        int now = 0;
        while(t[mt1].s[now].next!=1004&&t[mt1].s[now].next!=0)
        {
            now = t[mt1].s[now].next;
            if(sels[now]==0)
                trash.push_back(now);
        }
        ps.resize(1100);
        memset(&ps[0],0,1100*sizeof(dou_ll));
        ps_sz = ins(ps,trash);
        trash.clear();
        int ms = -1;
        now = 0;
        while(ps[now].next!=1004&&ps[now].next!=0)
        {
            int _s = ps[now].next;
            now = ps[now].next;
            if(sels[_s]==1) continue;
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
        sels[ms] = 1;
        c[_c].s.push_back(ms);
        trash.clear();
        now = 0;
        while(s[ms].t[now].next!=1004&&s[ms].t[now].next!=0)
        {
            now = s[ms].t[now].next;
            if(selt[now]==0)
                trash.push_back(now);
        }
        pt.resize(1100);
        memset(&pt[0],0,1100*sizeof(dou_ll));
        pt_sz = ins(pt,trash);
        trash.clear();
        del(ps,ms);
        ps_sz--;
        del(pt,mt1);
        pt_sz--;
        for(int i=1;i<=g.nStu;i++)
        {
            s[i].ssz-=del(s[i].s,ms);
            s[i].tsz-=del(s[i].t,mt1);
        }
        for(int _t=1;_t<=g.nProf;_t++)
        {
            t[_t].ssz-=del(t[_t].s,ms);
        }

        //ps and pt are defined
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
                    if(sels[i]==1) continue;

                    int check = 1;
                    for(auto _t: c[_c].t)
                    {
                        if(g.prf[_t][i]<g.minMachProf)
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
                    /*
                    lis[i] = intersection(ps,s[i].s); //len(intersection) of student
                    lis1[i] = ps_sis[i];
                    if(lis[i]!=lis1[i])
                    {
                        cout<<"Sth wrong ps_sis.";exit(0);
                    }
                    */
                    lis[i] = ps_sis[i];
                    /*
                    lit[i] = intersection(pt,s[i].t); //len(intersection) of teacher
                    lit1[i] = pt_sit[i];
                    if(lit[i]!=lit1[i])
                    {
                        cout<<"Sth wrong pt_sit.";exit(0);
                    }
                    */
                    lit[i] = pt_sit[i];

                    if(lis[i] + cs + 1 < g.miniStu)
                        continue;
                    if(lit[i] + ct < g.miniProf)
                        continue;
                    if(ms==-1)
                        ms = i;
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
                    //s[i].ssz -= del(s[i].s,ms);
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
                sels[ms] = 1;

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
                    if(selt[_t]==1) continue;

                    int check = 1;
                    for (auto i: c[_c].s)
                    {
                        if(g.prf[_t][i]<g.minMachProf)
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

                    /*
                    lis[_t] = intersection(ps,t[_t].s);
                    lis1[_t] = ps_tts[_t];
                    if(lis[_t]!=lis1[_t])
                    {
                        cout<<"Sth wrong ps_tts.";exit(0);
                    }
                    */
                    lis[_t] = ps_tts[_t];
                    if(lis[_t] + cs <g.miniStu)
                        continue;
                    if(mt==-1)
                        mt = _t;
                    else if (lis[_t]>lis[mt])
                        mt = _t;
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
                selt[mt] = 1;
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
        if(sels[i]==1)
        {
            for(int _c=1;_c<=g.nC;_c++)
            {
                c[_c].ps_sz -= del(c[_c].ps,i);
            }
        }
    }

    for(int _t = 1; _t <= g.nProf ; _t++)
    {
        if(selt[_t]==1)
        {
            for(int _c=1;_c<=g.nC;_c++)
            {
                c[_c].pt_sz -= del(c[_c].pt,_t);
            }
        }
    }

    for(int _t = 1; _t <= g.nProf ; _t++)
    {
        if(selt[_t]==0)
        {
            int mc = -1;
            for(int _c=1;_c<=g.nC;_c++)
            {
                if(c[_c].t.size()==g.maxProf) continue;
                int check = 1;
                for(auto j: c[_c].s)
                {
                    if(g.prf[_t][j]<g.minMachProf)
                    {
                        check = 0;
                        break;
                    }
                }
                if (check==0) continue;

                lis[_c] = intersection(c[_c].ps,t[_t].s);

                if(mc==-1)
                    mc=_c;
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
            selt[_t] = 1;
        }
    }

    for(int i=1;i<=g.nStu;i++)
    {
        if(sels[i]==0)
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
                    if(g.prf[_t][i]<g.minMachProf)
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
                    mc = _c;
            }
            if(mc==-1) return 0;
            c[mc].s.push_back(i);
            for(int _c=1;_c<=g.nC;_c++)
            {
                c[_c].ps_sz -= del(c[_c].ps,i);
            }
            sels[i] = 1;
        }
    }

    return 1;
}

bool arr1[100'000'000];
bool arr2[100'000'000];

vector<int> prj_val;
vector<int> prf_val;

void input()
{
    cin>>g.nStu>>g.nProf>>g.nC;
    cin>>g.miniStu>>g.maxStu>>g.miniProf>>g.maxProf>>g.minMatchStu>>g.minMachProf;
    for(int i=1;i<=g.nStu;i++)
    {
        for(int j=1;j<=g.nStu;j++)
        {
            int gg;
            cin>>gg;
            if (i==j)
            {
                g.prj[i][j] = -1;
                continue;
            }
            g.prj[i][j] = gg;
            if(gg<100'000'000)
            {
                if(arr1[gg]==0)
                {
                    arr1[gg] = 1;
                    prj_val.push_back(gg);
                }
            }
            else
            {
                prj_val.push_back(gg);
            }
        }
    }
    for(int _t=1;_t<=g.nProf;_t++)
    {
        for (int i=1;i<=g.nStu;i++)
        {
            int gg = 0;
            cin>>gg;
            g.prf[_t][i] = gg;
            if(gg<100'000'000)
            {
                if(arr2[gg]==0)
                {
                    arr2[gg] = 1;
                    prf_val.push_back(gg);
                }
            }
            else
            {
                prf_val.push_back(gg);
            }
        }
    }
    for(int i=1;i<=g.nStu;i++)
    {
        int gg; cin>>gg;
        guide[gg] = 1;
        g.prf[gg][i] = -1;
    }
    sort(prj_val.begin(),prj_val.end());
    sort(prf_val.begin(),prf_val.end());
    prj_val.resize(std::distance(prj_val.begin(),std::unique(prj_val.begin(), prj_val.end())));
    prf_val.resize(std::distance(prf_val.begin(),std::unique(prf_val.begin(), prf_val.end())));
    sort(prj_val.begin(),prj_val.end());
    sort(prf_val.begin(),prf_val.end());
    int left = 0; int right = prj_val.size()-1;
    int mid = 0;
    int _e = prj_val[0];
    int _f = prf_val[0];

    clock_t BeginTime = clock();

    clock_t TrueSolve = 0;
    clock_t FalseSolve = 0;
    int ide = 0;
    int idf = 0;

    clock_t t;

    int check = 0;

    while(left<=right)
    {
        if (check==0)
            mid = left + (right-left)/4;
        else
            mid = left + (right-left)/2;
        t = clock();
        if (solve(prj_val[mid],_f)==1)
        {
            check = 0;
            TrueSolve += clock()-t;
            left = mid + 1;
            _e = max(prj_val[mid],_e);
            ide = mid;
        }
        else
        {
            check = 1;
            FalseSolve += clock()-t;
            right = mid - 1;
        }
    }
    left = 0;right = prf_val.size()-1;
    mid = 0;
    check = 0;
    while(left<=right)
    {
        if (check==0)
            mid = left + (right-left)/4;
        else
            mid = left + (right-left)/2;

        mid = left + (right-left)/4;
        t = clock();
        if(solve(_e,prf_val[mid])==1)
        {
            check = 0;
            _f = max(prf_val[mid],_f);
            left = mid + 1;
            idf = mid;
            TrueSolve += clock()-t;
        }
        else
        {
            check = 1;
            FalseSolve += clock()-t;
            right = mid - 1;
        }
    }

    if(solve(_e,_f)==0)
    {
        cout<<"No solution"<<el;
        exit(0);
    }

    cout<<"Maximum value of e and f are:\n"<<_e<<" "<<_f<<"\n\n";

    int ans = 0;
    /*
    cout<<"Index of e: "<<ide<<el;
    cout<<"Index of f: "<<idf<<el;
    cout<<"True solve time: "<<double(TrueSolve)/double(CLOCKS_PER_SEC)<<"s.";
    cout<<"False solve time: "<<double(FalseSolve)/double(CLOCKS_PER_SEC)<<"s.";
    */

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
