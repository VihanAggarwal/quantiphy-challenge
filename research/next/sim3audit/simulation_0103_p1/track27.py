# Person tracking in 0027: abs diff from median bg in ROI around the walk path; split person vs shadow.
import cv2, numpy as np, pandas as pd
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0027.mp4')
fr=[]
while True:
    ok,img=cap.read()
    if not ok: break
    fr.append(img)
fr=np.array(fr).astype(np.float32)
y0,y1,x0,x1=300,480,350,560
roi=fr[:,y0:y1,x0:x1]
bg=np.median(roi,axis=0)
rows=[]
for i in range(len(roi)):
    f=roi[i]
    diff=np.abs(f-bg).max(axis=2)
    bright=(f.mean(axis=2)-bg.mean(axis=2))  # shirt brighter
    dark=(bg.mean(axis=2)-f.mean(axis=2))    # shadow / pants darker
    m=(diff>18).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    # person = component(s) whose bbox contains bright shirt pixels; shirt mask
    shirt=(bright>25)
    ys,xs=np.nonzero(shirt)
    if len(xs)<5: continue
    sx,sy=xs.mean(),ys.mean()
    # person column band: pixels of diff mask within +-12 px of shirt x and y within [sy-25, sy+45], excluding shadow which lies to the right-down
    band=np.zeros_like(m); 
    xa,xb=int(sx-10),int(sx+11); ya,yb=int(sy-25),int(sy+50)
    band[ya:yb,xa:xb]=1
    pm=(m*band).astype(bool)
    pys,pxs=np.nonzero(pm)
    rows.append(dict(frame=i,shirt_x=sx+x0,shirt_y=sy+y0,shirt_n=len(xs),shirt_top=ys.min()+y0,
                     ptop=pys.min()+y0,pbot=pys.max()+y0,pcx=pxs.mean()+x0,pcy=pys.mean()+y0))
df=pd.DataFrame(rows)
df.to_csv('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p1/p27.csv',index=False)
print(df.round(1).to_string())
