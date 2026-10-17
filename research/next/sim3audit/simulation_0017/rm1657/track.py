import cv2, numpy as np, json
V='/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0017_segmented.mp4'
c=cv2.VideoCapture(V); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY))
fr=np.array(fr)  # 101x1080x1080 uint8 ~118MB in RAM only
fg=fr<235
static=np.median(fg.astype(np.uint8),axis=0)>0.5
np.save('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0017/rm1657/static_mask.npy',np.packbits(static))
out=[]
for i in range(len(fr)):
    m=fg[i]&~static
    m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: out.append(None); continue
    k=1+np.argmax(st[1:,4])
    pm=lab==k
    ys,xs=np.nonzero(pm)
    # torso band: rows 430..540
    band=(ys>440)&(ys<530)
    tor=xs[band].mean() if band.sum()>50 else np.nan
    # head: top 25 rows of mask
    top=ys.min(); hb=ys<top+30; headx=xs[hb].mean()
    out.append(dict(i=i,top=int(top),bot=int(ys.max()),x0=int(xs.min()),x1=int(xs.max()),torso_x=float(tor),head_x=float(headx),area=int(pm.sum())))
json.dump(out,open('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0017/rm1657/track.json','w'),indent=0)
for o in out[::5]: print(o)
