import cv2, numpy as np, sys
v=sys.argv[1]
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/%s.mp4'%v)
F=[]
while True:
    ok,f=c.read()
    if not ok: break
    F.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32))
k0=int(sys.argv[2])
# templates given as x,y,w,h at frame k0
T=dict(letters=(None),)
import json
boxes=json.loads(sys.argv[3])
for name,(x,y,w,h) in boxes.items():
    tpl=F[k0][y:y+h,x:x+w]
    xs=[];ks=[]
    for k in range(1,len(F)):
        # search window around predicted
        res=cv2.matchTemplate(F[k][max(0,y-10):y+h+10,:],tpl,cv2.TM_CCOEFF_NORMED)
        _,mv,_,ml=cv2.minMaxLoc(res)
        if mv<0.9: continue
        px,py=ml
        # subpixel parabola in x
        if 0<px<res.shape[1]-1:
            a,b,cc=res[py,px-1],res[py,px],res[py,px+1]
            dx=0.5*(a-cc)/(a-2*b+cc)
        else: dx=0
        xs.append(px+dx); ks.append(k)
    ks=np.array(ks); xs=np.array(xs)
    p=np.polyfit(ks,xs,1)
    print('%-10s n=%2d v=%.3f px/frame  resid %.2f'%(name,len(ks),p[0],np.std(xs-np.polyval(p,ks))))
