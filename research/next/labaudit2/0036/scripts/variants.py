import numpy as np, json
T=json.load(open('scripts/trk_bg.json')); Z=json.load(open('scripts/size2.json'))
R=0.02; c0=np.array([640.,360.])
def cap(k): return int(np.floor(k*25/24+0.5))
def ray(u,v,f):
    r=np.array([(u-c0[0])/f,(v-c0[1])/f,1.]); return r/np.linalg.norm(r)
ks=list(range(16,36)); tc=np.array([cap(k) for k in ks],float)
Uo=np.array([[T['captured_0036'][str(k)]['cx'],T['captured_0036'][str(k)]['cy']] for k in ks])
Ua=np.array([[np.mean([T[v][str(k)]['cx'] for v in T]),np.mean([T[v][str(k)]['cy'] for v in T])] for k in ks])
do=np.array([Z['captured_0036'][str(k)]['d'] for k in ks]); do[-1]=Z['captured_0036s']['35']['d']
ds=np.array([Z['captured_0036s'][str(k)]['d'] for k in ks])
for f in [711.,766.]:
    print('== f',f)
    for clickname,U in [('raw_o',Uo),('raw_avg',Ua)]:
        for dname,dd,excl in [('d_o',do,[]),('d_o_no35',do,[35]),('d_s',ds,[17,33])]:
            for deg in [1,2]:
                sel=np.array([(k>=18 and k not in excl) for k in ks])
                p=np.polyfit(tc[sel],1/dd[sel],deg)   # 1/d ∝ r
                inv=np.polyval(p,tc)
                K09=(1.010+R)/np.polyval(p,22.5); K14=(0.716+R)/np.polyval(p,35.)
                w=np.clip((tc-22.5)/12.5,0,1); rc=(K09*(1-w)+K14*w)*inv
                Ps=np.array([(rc[i]-R)*ray(*U[i],f) for i in range(len(ks))])
                fd=lambda n:(lambda i:100*25*np.linalg.norm(Ps[i+1]-Ps[i]))(list(tc).index(n))
                rad=lambda n:(lambda i:100*25*(rc[i+1]-rc[i]))(list(tc).index(n))
                print('  %-7s %-9s deg%d  K09 %.1f K14 %.1f  v0.9 %.1f/%.1f  v1.4 %.1f   rad0.9 %.1f rad1.4 %.1f'%(clickname,dname,deg,K09,K14,fd(22),fd(23),fd(35),rad(22),rad(35)))
