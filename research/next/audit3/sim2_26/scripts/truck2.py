import sys; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/audit3/sim2_26/scripts')
from util import *
F=frames('0187')
G=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32) for f in F]
bg=np.maximum.reduce([np.abs(G[0]-G[i]) for i in range(1)])
res=[]
for i in range(8,58):
    a=G[i-1]; b=G[i]
    # truck mask in frame i-1: diff from both frame0 and frame59 backgrounds
    da=np.minimum(np.abs(a-G[0]),np.abs(a-G[59]))
    m=(da>15)
    m[:300]=False; m[930:]=False
    ys,xs=np.nonzero(m)
    if len(xs)<5000: continue
    x0,x1=np.percentile(xs,1),np.percentile(xs,99)
    x0=int(max(x0,0)); x1=int(min(x1,1919))
    y0,y1=320,920
    tpl=cv2.Sobel(a[y0:y1,x0:x1],cv2.CV_32F,1,0)
    best=(-2,0)
    for s in range(0,140):
        if x1+s>1919: 
            w=1919-s-x0
            if w<200: break
            T=tpl[:,:w]; B=cv2.Sobel(b[y0:y1,x0+s:x0+s+w],cv2.CV_32F,1,0)
        else:
            T=tpl; B=cv2.Sobel(b[y0:y1,x0+s:x1+s],cv2.CV_32F,1,0)
        # exclude static: weight by mask
        mm=m[y0:y1,x0:x0+T.shape[1]]
        A=T*mm; Bm=B*mm
        c=(A*Bm).sum()/np.sqrt((A*A).sum()*(Bm*Bm).sum()+1e-9)
        if c>best[0]: best=(c,s)
    res.append((i,best[1],best[0]))
    print(i,best[1],round(float(best[0]),3),x0,x1)
r=np.array(res)
ok=(r[:,2]>0.5)
p=np.polyfit(r[ok,0],r[ok,1],1); print('fit shift(i)=',p, 'resid',np.std(r[ok,1]-np.polyval(p,r[ok,0])))
