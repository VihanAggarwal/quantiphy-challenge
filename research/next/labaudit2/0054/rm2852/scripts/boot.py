import sys, os, math, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import ballfit as B
r=B.fit('white',24,39,anchor=3.0735+0.033)
print('residuals (px):'); 
for c,rr in zip(r['cs'],r['res']): print(' c%d  du=%+.2f dv=%+.2f'%(c,rr[0],rr[1]))
tr0=B.track('white'); rng=np.random.default_rng(0)
out=[]
for b in range(150):
    tr={c:v+rng.normal(0,1.0,2) for c,v in tr0.items()}
    B.track=lambda kind,tr=tr: tr
    anc=3.0735+0.033+rng.normal(0,0.04)
    try: q=B.fit('white',24,39,anchor=anc)
    except Exception: continue
    P=B.model(q['q'],np.array([37/25,38/25,39/25]),q['th'],q['rho'],q['g'])
    out.append((np.linalg.norm(P[1]-P[0])*25,np.linalg.norm(P[2]-P[1])*25))
out=np.array(out)
print('bootstrap (1px pixel noise, 4cm anchor noise) n=%d: c37->38 %.3f +- %.3f ; c38->39 %.3f +- %.3f'%(len(out),out[:,0].mean(),out[:,0].std(),out[:,1].mean(),out[:,1].std()))
