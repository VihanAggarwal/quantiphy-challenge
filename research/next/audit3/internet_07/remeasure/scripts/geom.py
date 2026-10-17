import json,numpy as np
from lsq import least_squares
e=json.load(open('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/edges.json'))
el=json.load(open('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/edgesL.json'))
med=lambda A: float(np.median(np.array(A)[:,1]))
rows=[]
for i in range(55,80):
    R=np.array(e[str(i)]['R']); up=R[R[:,0]<880]; lo=R[R[:,0]>900]
    Rup=float(np.median(up[:,1])); Rlo=float(np.median(lo[:,1]))
    Lm=float(np.median(np.array(e[str(i)]['L'])[:,1])) if i>=69 else (med(el[str(i)]['Lmid']) if str(i) in el and 'Lmid' in el[str(i)] else np.nan)
    Ll=med(el[str(i)]['Llo']) if str(i) in el and 'Llo' in el[str(i)] else np.nan
    Lt=med(el[str(i)]['Ltop']) if str(i) in el and 'Ltop' in el[str(i)] else np.nan
    rows.append((i,Rup,Rlo,Lm,Ll,Lt))
rows=np.array(rows)
np.save('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/edges_tab.npy',rows)
for r in rows: print('%d Rup %.2f Rlo %.2f Lmid %.2f Llo %.2f Ltop %.2f  wmid %.2f wlo %.2f cmid %.2f clo %.2f'%(*r, r[1]-r[3], r[2]-r[4], (r[1]+r[3])/2,(r[2]+r[4])/2))
# fit width model on mid rows, frames 65-79
sel=(rows[:,0]>=65)&(rows[:,0]<=79)
c=(rows[sel,1]+rows[sel,3])/2; w=(rows[sel,1]-rows[sel,3])
def res(p):
    w0,cx,f=p; return w0*np.sqrt(1+((c-cx)/f)**2)-w
p=least_squares(res,[410,960,1400]).x
print('mid fit w0 %.1f cx %.1f f %.1f'%tuple(p), 'resid',np.round(res(p),2))
sel2=(rows[:,0]>=61)&(rows[:,0]<=79)
c2=(rows[sel2,2]+rows[sel2,4])/2; w2=(rows[sel2,2]-rows[sel2,4])
def res2(p):
    w0,cx,f=p; return w0*np.sqrt(1+((c2-cx)/f)**2)-w2
p2=least_squares(res2,[410,960,1400]).x
print('lo fit w0 %.1f cx %.1f f %.1f'%tuple(p2), 'resid',np.round(res2(p2),2))
