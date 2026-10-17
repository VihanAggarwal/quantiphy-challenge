# turtle masks in simulation_0159: median background, diff threshold, largest blob in lower region
import cv2, numpy as np, json
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0159.mp4')
frs=[]
while True:
    ok,f=cap.read()
    if not ok: break
    frs.append(f)
A=np.stack(frs).astype(np.int16)
bg=np.median(A,axis=0).astype(np.int16)
out={}
for i,f in enumerate(A):
    d=np.abs(f-bg).max(axis=2)
    m=(d>14).astype(np.uint8)
    m[:540,:]=0; m[915:,:]=0  # turtle band; shark above, seabed below
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    k=1+np.argmax(st[1:,4])
    mk=(lab==k)
    ys,xs=np.nonzero(mk)
    out[i]=dict(area=int(mk.sum()),xmin=int(xs.min()),xmax=int(xs.max()),ymin=int(ys.min()),ymax=int(ys.max()),cx=float(xs.mean()),cy=float(ys.mean()))
    if i in (0,12,24,36,40):
        ov=frs[i].copy(); ov[mk]=(0.5*ov[mk]+[0,0,127]).astype(np.uint8)
        cv2.imwrite(f'/home/user/quantiphy-challenge/research/next/sim3audit/group4/frames/t159_ov{i:02d}.png',ov[500:1000,900:1900])
for i in sorted(out): print(i,out[i])
json.dump(out,open('/home/user/quantiphy-challenge/research/next/sim3audit/group4/t159_bbox.json','w'))
