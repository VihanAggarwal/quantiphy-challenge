# Per-frame person features in 0027: foot (lowest person px), head top, shirt top/centroid, shadow tip.
import cv2, numpy as np, pandas as pd
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0027.mp4')
fr=[]
while True:
    ok,img=cap.read()
    if not ok: break
    fr.append(img)
fr=np.array(fr).astype(np.float32)
y0,y1,x0,x1=300,480,350,600
roi=fr[:,y0:y1,x0:x1]; bg=np.median(roi,axis=0)
rows=[]
for i in range(len(roi)):
    f=roi[i]; lum=f.mean(axis=2); bl=bg.mean(axis=2)
    bright=lum-bl; dark=bl-lum; diff=np.abs(f-bg).max(axis=2)
    shirt=bright>25
    ys,xs=np.nonzero(shirt); sx,sy=xs.mean(),ys.mean()
    # person mask: diff>12 in column band around shirt
    m=(diff>12)
    band=np.zeros_like(m); band[int(sy-30):int(sy+55),int(sx-9):int(sx+10)]=True
    # exclude shadow: shadow is dark and lies right of the feet; restrict person band to x<=sx+9
    pm=m&band
    pys,pxs=np.nonzero(pm)
    # head top: topmost row with >=2 px in person mask above the shirt top
    rowsum=pm.sum(axis=1); rr=np.nonzero(rowsum>=2)[0]
    top=rr.min(); bot=rr.max()
    # shadow: dark>25 pixels with x > foot x + 4 and y within [sy-40, sy+60]
    sm=(dark>25); sm[:, :int(sx+6)]=False
    n,lab,st,cen=cv2.connectedComponentsWithStats(sm.astype(np.uint8))
    k=1+np.argmax(st[1:,4]) if n>1 else None
    sys_,sxs=np.nonzero(lab==k)
    dirv=np.array([0.93,-0.37]); proj=sxs*dirv[0]+sys_*dirv[1]
    j=np.argsort(proj)[-5:]
    tipx,tipy=sxs[j].mean(),sys_[j].mean()
    rows.append(dict(frame=i,shirt_x=sx+x0,shirt_y=sy+y0,shirt_top=ys.min()+y0,head_top=top+y0,foot=bot+y0,
                     foot_x=pxs[pys>=bot-1].mean()+x0,tip_x=tipx+x0,tip_y=tipy+y0,shadow_area=st[k,4]))
df=pd.DataFrame(rows)
df.to_csv('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p1/p27b.csv',index=False)
print(df.round(1).to_string())
