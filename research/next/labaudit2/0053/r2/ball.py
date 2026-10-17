import cv2,numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/captured_0053x.mp4')
x0,x1,y0,y1=930,1040,320,420
acc=[]
while True:
    ok,f=c.read()
    if not ok: break
    acc.append(f[y0:y1,x0:x1].astype(float))
A=np.array(acc)
# per-frame alpha
gr=A[...,1]-np.maximum(A[...,0],A[...,2])
al=np.clip(1-gr/252,0,1)
for i in [0,10,20,30,40,47]:
    a=al[i]
    ys,xs=np.nonzero(a>0.5)
    print(i,'area',a.sum().round(1),'eqdiam',(2*np.sqrt(a.sum()/np.pi)).round(2),'w',a.sum(0).max().round(1) if False else (xs.max()-xs.min()+1),'h',ys.max()-ys.min()+1,'cx',(a*np.arange(x1-x0)).sum()/a.sum()+x0,'cy',(a.T*np.arange(y1-y0)).sum()/a.sum()+y0)
a=al.mean(0)
print('mean area',a.sum(),'eq diam',2*np.sqrt(a.sum()/np.pi))
print('max row width',a.sum(1).max(),'max col height',a.sum(0).max())
# fit ellipse to contour of mean alpha
m=(a>0.5).astype(np.uint8)
cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
cnt=max(cs,key=cv2.contourArea)
print('ellipse',cv2.fitEllipse(cnt))
