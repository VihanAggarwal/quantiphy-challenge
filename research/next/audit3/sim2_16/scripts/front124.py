import cv2,numpy as np
c=cv2.VideoCapture('data/QuantiPhy/simulation_0124_segmented.mp4')
F=[]
for i in range(20):
    ok,im=c.read(); F.append(im.astype(np.int16))
def comps(im):
    d=(255-im).sum(2); m=(d>60).astype(np.uint8)
    nl,lab,st,cen=cv2.connectedComponentsWithStats(m)
    ks=sorted([k for k in range(1,nl) if st[k][4]>200],key=lambda k:cen[k][0])
    out=[]
    for k in ks:
        ys,xs=np.nonzero(lab==k); out.append(np.stack([xs,ys],1).astype(float))
    return out  # left=red, right=black
# headings from fully-visible frames: velocity directions via centroid differences
cent={}
pts={}
for i in range(20):
    cs=comps(F[i]); pts[i]=cs; cent[i]=[p.mean(0) for p in cs]
def head(car,i):
    # use direction of centroid motion between frames (i, i+1) averaged with (i-1,i); for early frames extrapolate from 5..9 headings
    return None
# heading angle per frame for frames>=5 using minAreaRect long axis oriented along motion
ang={0:{},1:{}}
for car in (0,1):
    for i in range(5,19):
        (cx,cy),(w,h),a=cv2.minAreaRect(pts[i][car].astype(np.float32))
        v=cent[i+1][car]-cent[i-1][car]; th=np.arctan2(v[1],v[0])
        ang[car][i]=th
# extrapolate heading back to frames 1-4 linearly from 5-9
res={}
for car in (0,1):
    fr=np.arange(5,10); th=np.array([ang[car][i] for i in fr]); p=np.polyfit(fr,th,1)
    for i in range(1,5): ang[car][i]=np.polyval(p,i)
# calibrate front offset and lateral offset in visible frames 6..15
for car in (0,1):
    fo=[];
    for i in range(6,16):
        u=np.array([np.cos(ang[car][i]),np.sin(ang[car][i])]); n=np.array([-u[1],u[0]])
        P=pts[i][car]; c0=cent[i][car]
        s=(P-c0)@u; fo.append(np.percentile(s,99.5))
    res[car]=np.median(fo)
    print('car',car,'front offset from centroid along heading (px) median %.2f spread %.2f'%(res[car],np.std(fo)))
est={}
for i in range(1,12):
    est[i]=[]
    for car in (0,1):
        u=np.array([np.cos(ang[car][i]),np.sin(ang[car][i])]); n=np.array([-u[1],u[0]])
        P=pts[i][car]
        front=np.percentile(P@u,99.5)
        # lateral centre: use rows near the front part (within 40px of front) -> mid of lateral extent
        sel=(P@u)>front-40
        lat=0.5*(np.percentile(P[sel]@n,0.5)+np.percentile(P[sel]@n,99.5))
        cpos=(front-res[car])*u+lat*n
        est[i].append(cpos)
    d=np.linalg.norm(est[i][0]-est[i][1])
    dc=np.linalg.norm(cent[i][0]-cent[i][1])
    print(i,'front-based dist %.1f  centroid dist %.1f'%(d,dc), 'red',np.round(est[i][0],1),'black',np.round(est[i][1],1))
