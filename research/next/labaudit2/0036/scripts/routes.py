import numpy as np, json
T=json.load(open('scripts/trk_bg.json'))
Z=json.load(open('scripts/size2.json'))
f=711.; c0=np.array([640.,360.]); R=0.02
def cap(k): return int(np.floor(k*25/24+0.5))
def ray(u,v,f=f):
    r=np.array([(u-c0[0])/f,(v-c0[1])/f,1.]); return r/np.linalg.norm(r)
V='captured_0036'
ks=list(range(14,36))
U=np.array([[T[V][str(k)]['cx'],T[V][str(k)]['cy']] for k in ks])
# render-averaged centroid
Ua=np.array([[np.mean([T[v][str(k)]['cx'] for v in T]),np.mean([T[v][str(k)]['cy'] for v in T])] for k in ks])
d=np.array([Z[V][str(k)]['d'] for k in ks]); d[ks.index(35)]=Z['captured_0036s']['35']['d']
tc=np.array([cap(k)/25 for k in ks])
print('video->capture', [(k,cap(k)) for k in ks])
# stated
def click(t):
    n=t*25; lo=int(np.floor(n)); hi=int(np.ceil(n))
    kv=[k for k in ks if cap(k) in (lo,hi)]
    return Ua[[ks.index(k) for k in kv]].mean(0), kv
for F in [711.,766.]:
    print('==== f',F)
    c09,kv09=click(0.9); c14,kv14=click(1.4)
    print('click 0.9',c09,kv09,' 1.4',c14,kv14)
    S09=1.010*ray(*c09,f=F); S14=0.716*ray(*c14,f=F)
    C09=(1.010+R)*ray(*c09,f=F); C14=(0.716+R)*ray(*c14,f=F)
    print('disp surface %.2f cm  centre %.2f cm'%(100*np.linalg.norm(S14-S09),100*np.linalg.norm(C14-C09)))
    # size route
    K09=(1.010+R)*np.interp(22.5,[cap(k) for k in ks],d)  # d at capture 22.5
    K14=(0.716+R)*d[ks.index(34)]
    print('K from 0.9: %.2f  from 1.4: %.2f'%(K09,K14))
    K=0.5*(K09+K14)
    rc=K/d
    P=np.array([rc[i]*ray(*Ua[i],f=F) for i in range(len(ks))])
    # line route
    D=C14-C09
    Pl=[]
    for i in range(len(ks)):
        r=ray(*Ua[i],f=F)
        # minimize |C09+s D - t r|
        A=np.stack([D,-r],1); s,t=np.linalg.lstsq(A,-C09,rcond=None)[0]
        Pl.append(C09+s*D)
    Pl=np.array(Pl)
    for name,PP in [('size',P),('line',Pl)]:
        print('--',name)
        rr=np.linalg.norm(PP,axis=1)
        for i in range(len(ks)-1):
            dt=tc[i+1]-tc[i]
            vv=(PP[i+1]-PP[i])/dt
            rad=(rr[i+1]-rr[i])/dt
            print('  vid %2d->%2d cap %2d->%2d  r=%.3f  speed %6.1f  radial %6.1f  lat %6.1f'%(ks[i],ks[i+1],cap(ks[i]),cap(ks[i+1]),rr[i],100*np.linalg.norm(vv),100*rad,100*np.sqrt(max(np.linalg.norm(vv)**2-rad**2,0))))
