import json,numpy as np
from lsq import least_squares
B=json.load(open('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/bands.json'))
fr=np.arange(55,80)
def band(b,side): return np.array([B[str(i)][b][0 if side=='L' else 1] for i in fr],float)
out={}
for b in ('lo','lo2','top','mid'):
    L=band(b,'L'); R=band(b,'R')
    ok=~np.isnan(L)&(fr>=62)
    c=(L+R)/2; w=R-L
    def res(p): return p[0]*np.sqrt(1+((c[ok]-p[1])/p[2])**2)-w[ok]
    p=least_squares(res,[410,960,1500]).x
    rr=res(p)
    # center from R only using model (iterate)
    cR=R-p[0]/2
    for _ in range(10): cR=R-p[0]*np.sqrt(1+((cR-p[1])/p[2])**2)/2
    cL=L+p[0]/2
    for _ in range(10): cL=L+p[0]*np.sqrt(1+((cL-p[1])/p[2])**2)/2
    print(b,'w0 %.1f cx %.1f f %.0f rms %.2f'%(p[0],p[1],p[2],np.sqrt(np.mean(rr**2))))
    out[b]=dict(c=c.tolist(),cR=cR.tolist(),cL=cL.tolist(),p=p.tolist())
    for i,a,bb,cc in zip(fr,c,cR,cL): print('  %d c %.2f cR %.2f cL %.2f'%(i,a,bb,cc))
json.dump(out,open('/home/user/quantiphy-challenge/research/next/audit3/internet_07/remeasure/centers.json','w'))
