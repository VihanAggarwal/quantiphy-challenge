import numpy as np, cv2, sys
from load import frames
c=sys.argv[1]; ref=int(sys.argv[2]); pts=eval(sys.argv[3]); v0=float(sys.argv[4])
F=frames(c); G=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32) for f in F]
r=12
for k,p in pts.items():
    T=G[ref][p[1]-r:p[1]+r+1,p[0]-r:p[0]+r+1]
    tr=[]
    for i in range(2,len(G)):
        px=p[0]+v0*(i-ref); xa=int(px)-12; xb=int(px)+12
        if xa-r<0 or xb+r>=2560: continue
        S=G[i][p[1]-r-4:p[1]+r+5, xa-r:xb+r+1]
        R=cv2.matchTemplate(S,T,cv2.TM_CCOEFF_NORMED)
        _,mv,_,ml=cv2.minMaxLoc(R); x,y=ml; dx=0
        if 0<x<R.shape[1]-1: a,b,cc=R[y,x-1],R[y,x],R[y,x+1]; dx=0.5*(a-cc)/(a-2*b+cc)
        tr.append((i,xa+x+dx,mv))
    tr=np.array(tr)
    ok=tr[:,2]>0.8
    for it in range(3):
        co=np.polyfit(tr[ok,0]-ref,tr[ok,1],1); res=tr[:,1]-np.polyval(co,tr[:,0]-ref)
        ok=(tr[:,2]>0.8)&(abs(res)<1.5)
    print('%-9s x(ref)=%.2f speed=%.3f px/frame  resid %.2f  n=%d/%d'%(k,co[1],co[0],np.std(res[ok]),ok.sum(),len(tr)))
