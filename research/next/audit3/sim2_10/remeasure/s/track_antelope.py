import cv2, numpy as np, sys
V='/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0246.mp4'
c=cv2.VideoCapture(V); F=[]
while True:
    ok,f=c.read()
    if not ok: break
    F.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY))
F=np.array(F); n=len(F)
# background = median over frames (objects move) 
bg=np.median(F[::4],axis=0).astype(np.float32)
# torso template from frame 0: torso region approx x 470..760, y 510..630 (full res) -- determine by diff mask
d=np.abs(F[0].astype(np.float32)-bg)
ys,xs=np.where(d>25)
print('frame0 diff bbox', xs.min(),xs.max(),ys.min(),ys.max())
def track(x0,x1,y0,y1,ref=0,search=None):
    T=F[ref][y0:y1,x0:x1]
    out=[]
    for i in range(n):
        R=cv2.matchTemplate(F[i],T,cv2.TM_CCOEFF_NORMED)
        # restrict to same rows +-20
        mask=np.full(R.shape,-1.0,np.float32)
        ylo=max(0,y0-25); yhi=min(R.shape[0],y0+25)
        mask[ylo:yhi,:]=R[ylo:yhi,:]
        _,mv,_,ml=cv2.minMaxLoc(mask)
        # subpixel parabola in x
        x,y=ml
        if 0<x<R.shape[1]-1:
            a,b,cc=mask[y,x-1],mask[y,x],mask[y,x+1]
            den=a-2*b+cc
            dx=0.5*(a-cc)/den if den!=0 else 0
        else: dx=0
        out.append((x+dx,y,mv))
    return np.array(out)
for name,box,ref in [('torso_f0',(470,700,520,620),0),('torso_f37',None,37),('head_f0',(840,940,540,620),0)]:
    if box is None:
        continue
    t=track(*box,ref=ref)
    xs=t[:,0]; p=np.polyfit(np.arange(n),xs,1)
    print(name,'fit px/f %.3f'%p[0],'end-to-end %.2f'%((xs[-1]-xs[0])/(n-1)),'minscore %.3f'%t[:,2].min(), 'y range',t[:,1].min(),t[:,1].max())
np.save('/tmp/claude-0/bg0246.npy',bg) if False else None
