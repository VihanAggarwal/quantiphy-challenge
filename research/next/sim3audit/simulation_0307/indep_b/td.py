import numpy as np, cv2, sys
from load import frames
c=sys.argv[1]
F=frames(c); G=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32) for f in F]
ref=25
pts={'podN_top':(1103,570),'podN_bot':(1103,898),'tail_tip':(1666,736),'stab_top':(1640,640),'stab_bot':(1640,833),'cap_top':(1290,378),'cap_bot':(1290,1088)}
if len(sys.argv)>2: pts=eval(sys.argv[2])
r=14
out={}
for k,p in pts.items():
    T=G[ref][p[1]-r:p[1]+r+1,p[0]-r:p[0]+r+1]
    track={}
    for i in range(2,len(G)):
        # predicted
        px=p[0]-34.45*(i-ref) if c in('0284','0286') else p[0]-43*(i-ref)
        xa=int(px)-60; xb=int(px)+60
        if xa-r<0 or xb+r>=2560: continue
        S=G[i][p[1]-r-6:p[1]+r+7, xa-r:xb+r+1]
        R=cv2.matchTemplate(S,T,cv2.TM_CCOEFF_NORMED)
        _,mv,_,ml=cv2.minMaxLoc(R)
        x,y=ml
        # subpixel
        dx=0;dy=0
        if 0<x<R.shape[1]-1: a,b,cc=R[y,x-1],R[y,x],R[y,x+1]; dx=0.5*(a-cc)/(a-2*b+cc)
        if 0<y<R.shape[0]-1: a,b,cc=R[y-1,x],R[y,x],R[y+1,x]; dy=0.5*(a-cc)/(a-2*b+cc)
        X=xa+x+dx; Y=p[1]-6+y+dy
        if mv>0.85: track[i]=(X,Y,mv)
    ii=np.array(sorted(track)); xs=np.array([track[i][0] for i in ii]); ys=np.array([track[i][1] for i in ii])
    A=np.c_[np.ones(len(ii)),ii-ref]; co=np.linalg.lstsq(A,xs,rcond=None)[0]; res=xs-A@co
    out[k]=(p,co[0],co[1],np.std(res),len(ii),ys.mean(),np.polyfit(ii-ref,ys,1)[0])
    print('%-9s x(ref)=%.2f speed=%.3f px/frame  resid %.2f  n=%d  y=%.1f dy/dfr=%.3f'%(k,co[0],co[1],np.std(res),len(ii),ys.mean(),out[k][6]))
np.save(f'td_{c}.npy',out,allow_pickle=True)
