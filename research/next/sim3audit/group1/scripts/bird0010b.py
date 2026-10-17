import cv2, numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0010.mp4'); fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
st=np.stack(fr).astype(np.int16); med=np.median(st,0)
cx,cy=960.0,977.0
pts=[]
for i,f in enumerate(fr):
    d=np.abs(f.astype(np.int16)-med).max(2)
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
    m=((d>45)&(g<70)).astype(np.uint8)
    m[:, :250]=0; m[950:,:]=0; m[:600,:]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,s,cen=cv2.connectedComponentsWithStats(m)
    if n<2: pts.append((i,np.nan,np.nan,0)); continue
    k=1+np.argmax(s[1:,4])
    pts.append((i,cen[k][0],cen[k][1],s[k][4]))
pts=np.array(pts)
for p in pts: print('%2d %.1f %.1f %d'%tuple(p))
np.save('scripts/bird0010b.npy',pts)
