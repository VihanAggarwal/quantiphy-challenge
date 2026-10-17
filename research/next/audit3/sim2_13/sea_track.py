import cv2, numpy as np, sys, json
c=sys.argv[1]; thr=float(sys.argv[2]) if len(sys.argv)>2 else 20
cap=cv2.VideoCapture(f'data/QuantiPhy/simulation_{c}.mp4')
fr=[]
while True:
    ok,im=cap.read()
    if not ok: break
    fr.append(im)
N=len(fr)
bg=np.median(np.stack(fr).astype(np.float32),axis=0)
if c in ('0157','0158'):
    bg[:,1450:]=np.median(np.stack(fr[38:]).astype(np.float32)[:,:,1450:],axis=0)
YMAX=780
res=[]
for i in range(N):
    d=np.abs(fr[i].astype(np.float32)-bg).max(axis=2)
    m=(d>thr).astype(np.uint8); m[YMAX:]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    objs=[]
    for k in range(1,n):
        x,y,w,h,a=st[k]
        if a<800: continue
        ys,xs=np.nonzero(lab==k)
        objs.append(dict(x0=int(x),x1=int(x+w-1),y0=int(y),y1=int(y+h-1),area=int(a),cx=float(cen[k][0]),cy=float(cen[k][1])))
    res.append(objs)
json.dump(res,open(f'research/next/audit3/sim2_13/seatrack_{c}_{int(thr)}.json','w'))
for i in range(N):
    print(i,[(o['x0'],o['x1'],o['y0'],o['y1'],o['area'],round(o['cx'])) for o in sorted(res[i],key=lambda o:-o['area'])[:3]])
