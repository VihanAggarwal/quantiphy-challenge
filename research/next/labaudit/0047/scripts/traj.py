import json, numpy as np, sys
D='/home/user/quantiphy-challenge/research/next/labaudit/0047/'
fn=sys.argv[1] if len(sys.argv)>1 else 'fit_x_711.json'
R=json.load(open(D+fn))
def tc(n): return n/25 if n<=11 else ((n+1)/25 if n<=35 else (n+2)/25)
ns=list(range(17,43))
X=[];T=[]
for n in ns:
    r=R[str(n)]; c=np.array(r['cone_c']); s=np.sin(r['alpha'])
    X.append(c/s); T.append(tc(n))
X=np.array(X); T=np.array(T)
print('pos in units of R (x,y,z), dc/R, step |dX|/R per frame, 25*step')
for i,n in enumerate(ns):
    st=np.linalg.norm(X[i+1]-X[i]) if i+1<len(ns) else np.nan
    dt=(T[i+1]-T[i]) if i+1<len(ns) else np.nan
    print(n, f'{T[i]:.2f}', np.round(X[i],2), f'{np.linalg.norm(X[i]):.2f}', f'step {st:.3f} dt {dt:.2f} v/R {st/dt if dt==dt else np.nan:.2f}')
# robust linear fit of position vs time over n20..34
for lo,hi in [(20,34),(22,32),(18,38),(24,40)]:
    m=(np.array(ns)>=lo)&(np.array(ns)<=hi)
    A=np.c_[np.ones(m.sum()),T[m],T[m]**2]
    co=np.linalg.lstsq(A,X[m],rcond=None)[0]
    v1=co[1]+2*co[2]*1.0
    print(lo,hi,'speed/R at 1.0s',np.linalg.norm(v1).round(3),'-> R from 2.1464:',(2.1464/np.linalg.norm(v1)).round(4), 'D cm',(200*2.1464/np.linalg.norm(v1)).round(1))
