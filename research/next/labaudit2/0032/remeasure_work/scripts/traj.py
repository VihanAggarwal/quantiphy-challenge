import numpy as np, sys, cv2
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0032/remeasure_work/scripts')
from geom import *
src=sys.argv[1] if len(sys.argv)>1 else '/home/user/quantiphy-challenge/data/QuantiPhy/captured_0032.mp4'
H=float(sys.argv[2]) if len(sys.argv)>2 else 17.8
cap=cv2.VideoCapture(src); fr=[]
while True:
    ok,fimg=cap.read()
    if not ok: break
    fr.append(fimg)
def blob(f):
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV).astype(int)
    roi=np.zeros(hsv.shape[:2],bool); roi[380:520,450:1000]=True
    m=((hsv[...,1]<60)&(hsv[...,2]>170)&roi).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n_,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); return cen[k]
def edges(p,off):
    mx=p.max(); mn=np.median(np.r_[p[:5],p[-5:]]); th=(mx+mn)/2
    idx=np.where(p>th)[0]; a=idx[0]; b=idx[-1]
    lo=a-1+(th-p[a-1])/(p[a]-p[a-1]); hi=b+(p[b]-th)/(p[b]-p[b+1])
    return lo+off, hi+off
rows=[]
for i in range(32,49):
    fimg=fr[i]; cx_,cy_=blob(fimg)
    hsv=cv2.cvtColor(fimg,cv2.COLOR_BGR2HSV).astype(float)
    Wm=(hsv[...,2]/255.0)*(1-hsv[...,1]/255.0)
    x0,y0=int(round(cx_)),int(round(cy_))
    vp=Wm[y0-25:y0+26, x0-2:x0+3].mean(1); hp=Wm[y0-3:y0+4, x0-30:x0+31].mean(0)
    t,_=edges(vp,y0-25); l,r=edges(hp,x0-30)
    rows.append((i,cx_,cy_,(l+r)/2,t,r-l))
rows=np.array(rows)
np.save('/home/user/quantiphy-challenge/research/next/labaudit2/0032/remeasure_work/white_rows_%s.npy'%src.split('_')[-1].split('.')[0],rows)
# capture index: video j>=36 -> c=j+1 (drop between 35 and 36), relative
def cap_idx(j): return j+1 if j>=36 else j
def pos(u,v):
    return on_plane(u,v,H-2.0)
for label,vsel in (('blob-centroid',lambda R: (R[1],R[2])),('profile u, top+r_pred',None)):
    P=[]
    for R in rows:
        if vsel is not None:
            u,v=vsel(R)
        else:
            u=R[3]; v=R[4]+10.4
            for _ in range(5):
                p=pos(u,v); rpx=f*2.0/np.linalg.norm(p); v=R[4]+rpx
        P.append(pos(u,v))
    P=np.array(P)
    print('==',label)
    for k in range(len(rows)-1):
        j=int(rows[k,0]); dc=cap_idx(j+1)-cap_idx(j)
        d=P[k+1]-P[k]; sp=np.linalg.norm(d)/dc*25
        rng=np.linalg.norm(P[k])
        print('v%d->%d (dc=%d) range %.1f  dX %.2f dY %.2f dZ %.2f  speed %.1f cm/s'%(j,j+1,dc,rng,*d,sp))
