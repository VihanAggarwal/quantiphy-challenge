import sys; sys.path.insert(0,'scripts')
from vid import frames
import cv2, numpy as np
F=frames('internet_0021_segmented')
G=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32) for f in F]
ref=G[0][300:470]; win=cv2.createHanningWindow(ref.shape[::-1],cv2.CV_32F)
cam={}
for i in range(0,107):
    sh,resp=cv2.phaseCorrelate(ref,G[i][300:470],win); cam[i]=sh
res=[]
for i in range(0,92):
    g=G[i][150:230]
    a=np.clip((235-g)/(235-60),0,1)   # darkness coverage
    a[a<0.15]=0
    colsum=a.sum(axis=0)
    xs=np.arange(len(colsum))
    on=np.where(colsum>0.5)[0]
    # subpixel extent: columns where colsum> half of median body-thickness at ends -> use coverage threshold 0.5 px
    x0,x1=on[0],on[-1]
    cx=(colsum*xs).sum()/colsum.sum()
    res.append((i,x0,x1,x1-x0+1,cx,cx-cam[i][0]))
r=np.array(res,float)
for row in r[::10]: print(np.round(row,2))
L=r[:,3]; fr=r[:,0]
pL=np.polyfit(fr,L,1); print('length fit',pL, 'L(0)',np.polyval(pL,0),'L(60)',np.polyval(pL,60))
# displacement 0->60 camera-corrected
d=r[60,5]-r[0,5]; print('disp px 0->60 corr',d,'uncorr',r[60,4]-r[0,4])
# metric displacement integrating per-frame scale
m=0
for k in range(1,61):
    m+=(r[k,5]-r[k-1,5])*40/np.polyval(pL,k-0.5)
print('metric disp 0-2s',m)
# avg speed over visible frames 0..90
m2=0
for k in range(1,91):
    m2+=(r[k,5]-r[k-1,5])*40/np.polyval(pL,k-0.5)
print('avg speed 0-90', m2/(90/29.97), 'with fps30', m2/3.0)
