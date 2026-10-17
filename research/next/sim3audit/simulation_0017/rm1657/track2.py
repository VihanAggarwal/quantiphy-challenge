import cv2, numpy as np, json
V='/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0017_segmented.mp4'
c=cv2.VideoCapture(V); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
fr=np.array(fr)
bg=np.median(fr,axis=0).astype(np.int16)
cv2.imwrite('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0017/rm1657/frames/seg_bg.png',bg.astype(np.uint8))
res=[]
for i in range(len(fr)):
    d=np.abs(fr[i].astype(np.int16)-bg).sum(2)
    m=(d>60).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); pm=lab==k
    ys,xs=np.nonzero(pm)
    top=ys.min()
    hb=(ys<top+45)
    hx=xs[hb].mean()
    # torso rows 440-520
    tb=(ys>440)&(ys<520)
    tx=xs[tb].mean() if tb.sum()>100 else np.nan
    res.append(dict(i=i,top=int(top),bot=int(ys.max()),x0=int(xs.min()),x1=int(xs.max()),head_x=float(hx),torso_x=float(tx),n=int(pm.sum())))
json.dump(res,open('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0017/rm1657/track2.json','w'))
for r in res[::4]: print(r)
