# body (carapace) track of the turtle in simulation_0159: mask -> big opening removes thin flippers -> centroid + extremes
import cv2, numpy as np, json
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0159.mp4')
frs=[]
while True:
    ok,f=cap.read()
    if not ok: break
    frs.append(f)
A=np.stack(frs).astype(np.int16)
bg=np.median(A,axis=0).astype(np.int16)
K=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(45,45))
res={}
for i,f in enumerate(A):
    d=np.abs(f-bg).max(axis=2)
    m=(d>14).astype(np.uint8); m[:540,:]=0; m[915:,:]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); mk=(lab==k).astype(np.uint8)
    mk=cv2.morphologyEx(mk,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
    body=cv2.morphologyEx(mk,cv2.MORPH_OPEN,K)
    ys,xs=np.nonzero(body)
    if len(xs)==0: continue
    ya,xa=np.nonzero(mk)
    res[i]=dict(bx=float(xs.mean()),by=float(ys.mean()),barea=int(len(xs)),bxmin=int(xs.min()),bxmax=int(xs.max()),
                xmin=int(xa.min()),xmax=int(xa.max()),ymin=int(ya.min()),ymax=int(ya.max()))
    if i in (12,24,36):
        ov=frs[i].copy(); ov[mk>0]=(0.6*ov[mk>0]+[0,0,100]).astype(np.uint8); ov[body>0]=(0.6*ov[body>0]+[0,100,0]).astype(np.uint8)
        cv2.imwrite(f'/home/user/quantiphy-challenge/research/next/sim3audit/group4/frames/t159_body{i:02d}.png',ov[550:950,1000:1900])
    np.save if False else None
    if i==24: np.save('/home/user/quantiphy-challenge/research/next/sim3audit/group4/t159_mask24.npy',mk)
for i in sorted(res): print(i,res[i])
json.dump(res,open('/home/user/quantiphy-challenge/research/next/sim3audit/group4/t159_track.json','w'))
