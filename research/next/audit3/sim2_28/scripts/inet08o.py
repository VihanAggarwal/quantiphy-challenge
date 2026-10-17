import cv2, numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0008.mp4')
i=0; rows=[]
while True:
    ok,f=c.read()
    if not ok: break
    if i%3==0:
        g=f.astype(np.float32).sum(axis=2)
        # dark objects on water: below horizon (y>450) dark pixels
        sub=g[440:540]
        m=(sub<150).astype(np.uint8)
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        comps=[(st[k][0],st[k][0]+st[k][2],st[k][1]+440,st[k][1]+st[k][3]+440,st[k][4]) for k in range(1,n) if st[k][4]>60]
        # sun position
        sun=(g>600)
        ys,xs=np.where(sun[:400])
        sc=(xs.mean(),ys.mean()) if len(xs) else (0,0)
        rows.append((i,comps,sc))
    i+=1
print('n frames',i)
for r in rows[::10]: print(r[0], r[1], np.round(r[2],1))
for r in rows:
    if r[0]>=240 and r[0]%15==0: print(r[0], r[1])
