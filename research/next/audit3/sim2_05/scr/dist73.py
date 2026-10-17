import cv2, numpy as np
v='simulation_0073'
bg=cv2.imread(f'/home/user/quantiphy-challenge/research/next/audit3/sim2_05/scr/bg_{v}.png').astype(int)
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
res={}
for i in range(72):
    ok,f=c.read()
    d=np.abs(f.astype(int)-bg).max(axis=2)
    out=[]
    for (xa,xb) in ((780,885),(903,934)):
        for thr in (12,25):
            m=d[:,xa:xb]>thr
            m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
            rows=np.where(m.sum(1)>=2)[0]; cols=np.where(m.sum(0)>=2)[0]
            # largest contiguous run of rows
            if len(rows)==0: out.append(None); continue
            br=np.split(rows,np.where(np.diff(rows)>4)[0]+1); r=max(br,key=len)
            mm=m[r[0]:r[-1]+1]; cols=np.where(mm.sum(0)>=2)[0]
            out.append((r[0],r[-1],xa+cols[0],xa+cols[-1]))
    res[i]=out
for i in (1,23,24,47,48,71):
    print(i,res[i])
import json; json.dump({k:[list(map(int,o)) if o else None for o in v_] for k,v_ in res.items()},open('/home/user/quantiphy-challenge/research/next/audit3/sim2_05/scr/d73.json','w'))
