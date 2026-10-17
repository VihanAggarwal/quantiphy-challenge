import json, numpy as np
rows=json.load(open('diam2_simulation_0254.json'))
R={int(r[0]):r for r in rows}
fr=np.array(sorted(i for i in R if 19<=i<=46))
cx=np.array([R[i][5] for i in fr]); cy=np.array([R[i][6] for i in fr])
# slope direction by line fit
A=np.c_[cx-cx.mean(),cy-cy.mean()]
u,s,vt=np.linalg.svd(A,full_matrices=False); d=vt[0]; 
if d[0]<0: d=-d
ang=np.degrees(np.arctan2(d[1],d[0])); print('slope angle in image (deg below horizontal):',ang)
s_=A@d; n_=A@np.array([-d[1],d[0]])
print('perp residual rms px',n_.std())
t=fr/24.0
for deg in (2,3):
    p=np.polyfit(t,s_,deg); res=s_-np.polyval(p,t)
    print('deg',deg,'coef',p,'rms',res.std())
    dp=np.polyder(p); ddp=np.polyder(dp)
    for tq in (0.5,0.75,1.0,1.5,1.75):
        # backward difference
        vb=(np.polyval(p,tq)-np.polyval(p,tq-1/24))*24
        print(f'  t={tq}: v_inst={np.polyval(dp,tq):.1f} v_back={vb:.1f} px/s  a={np.polyval(ddp,tq):.1f} px/s2')
    print('  time where v_inst=0 :',np.roots(dp))
# per-frame differences
ds=np.diff(s_); print('px/frame steps:',np.round(ds,2))
print('second diffs:',np.round(np.diff(ds),2))
