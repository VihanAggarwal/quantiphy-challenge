import numpy as np, json
f=711.; c0=np.array([640.,360.])
T=json.load(open('scripts/trk_o.json')); S=json.load(open('scripts/size2.json'))
n=np.load('scripts/plane_n.npy')
def orig(k): return k if k<=11 else (k+1 if k<=35 else k+2)
def ray(u,v):
    r=np.array([(u-c0[0])/f,(v-c0[1])/f,1.]); return r/np.linalg.norm(r)
def fit(ks,P,deg,tq):
    t=np.array([orig(k)/25. for k in ks]); X=np.array([P[k] for k in ks])
    out=[]
    for tt in tq:
        V=[]
        for j in range(3):
            c=np.polyfit(t,X[:,j],deg); V.append(np.polyval(np.polyder(c),tt))
        out.append(np.linalg.norm(V)*100)
    return out
routes={}
for hc in [0.154,0.157,0.160]:
    routes['plane hc=%.3f'%hc]={k:ray(T[str(k)]['cx'],T[str(k)]['cy'])*(hc/(n@ray(T[str(k)]['cx'],T[str(k)]['cy']))) for k in range(13,36)}
routes['size(top-shadow)']={k:ray(S[str(k)]['u'],S[str(k)]['vc'])*(S[str(k)]['rs']+0.02) for k in range(13,36)}
routes['size*1.04']={k:ray(S[str(k)]['u'],S[str(k)]['vc'])*(S[str(k)]['rs']*1.04+0.02) for k in range(13,36)}
tq=[0.88,0.9,0.92,1.38,1.4,1.42]
for name,P in routes.items():
    for (k0,k1,deg) in [(18,35,1),(18,35,2),(17,35,2),(19,34,1),(15,35,3)]:
        ks=list(range(k0,k1+1))
        v=fit(ks,P,deg,tq)
        print('%-18s fit %d-%d deg%d  v(0.88,0.90,0.92)=%s  v(1.38,1.40,1.42)=%s'%(name,k0,k1,deg,' '.join('%.1f'%x for x in v[:3]),' '.join('%.1f'%x for x in v[3:])))
    # displacement between t=0.9 (orig22.5 -> video 21.5) and 1.4 (orig 35 -> video 34)
    P215=(P[21]+P[22])/2
    print('   disp video21.5->34: %.1f cm'%(100*np.linalg.norm(P[34]-P215)))
