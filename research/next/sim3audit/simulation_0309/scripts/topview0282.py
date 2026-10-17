# 0282 (top-down 2D sibling): body length (snout-tail tip along x, central band) in px, and speed in px/frame
import cv2, numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0282.mp4'); F=[]
while True:
    ok,f=c.read()
    if not ok: break
    F.append(f)
bg=np.median(np.array(F[::6]).astype(np.float32),axis=0)
res=[]
for i,f in enumerate(F):
    d=np.abs(f.astype(np.float32)-bg).sum(2); m=(d>45).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    k=1+np.argmax(st[1:,4]); mm=(lab==k)
    ys,xs=np.nonzero(mm)
    # body centre line: row of head patch ~ median y of the leftmost 30 px
    xl=xs.min(); yc=np.median(ys[xs<xl+30])
    band=np.abs(ys-yc)<60
    res.append((i,xs[band].min(),xs[band].max(),yc, xs.min(), xs.max()))
R=np.array(res)
for r in R[::6]: print('%d head_x %d tail_x %d  len %d  yc %.0f'%(r[0],r[1],r[2],r[2]-r[1],r[3]))
ok=(R[:,1]>5)&(R[:,2]<2550)
hx=R[ok,1]; fr=R[ok,0]
A=np.polyfit(fr,hx,1); print('head x speed px/frame',A[0])
L=(R[ok,2]-R[ok,1]); print('len px pct10/50/90/max',np.percentile(L,[10,50,90,100]))
print('time to travel own length (frames) median/90pct', np.median(L)/abs(A[0]), np.percentile(L,90)/abs(A[0]))
print('-> length m at 1.29 m/s: median',np.median(L)/abs(A[0])/24*1.29,' p90',np.percentile(L,90)/abs(A[0])/24*1.29)
