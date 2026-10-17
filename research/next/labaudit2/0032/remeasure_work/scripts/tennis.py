import numpy as np, sys, cv2
sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0032/remeasure_work/scripts')
from geom import *
def capidx(j): return j+2 if j>=36 else j+1
for src in ('captured_0032.mp4','captured_0032x.mp4'):
    cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/'+src); fr=[]
    while True:
        ok,img=cap.read()
        if not ok: break
        fr.append(img)
    rows=[]
    for i in range(20,43):
        hsv=cv2.cvtColor(fr[i],cv2.COLOR_BGR2HSV).astype(int)
        roi=np.zeros(hsv.shape[:2],bool); roi[380:520,440:1000]=True
        m=((hsv[...,0]>18)&(hsv[...,0]<42)&(hsv[...,1]>100)&(hsv[...,2]>100)&roi).astype(np.uint8)
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        n_,lab,st,cen=cv2.connectedComponentsWithStats(m)
        k=1+np.argmax(st[1:,4]); x0,y0,w,h,a=st[k]
        # vertical centre: midpoint of top and bottom extents in central columns
        cols=np.arange(x0+w//3,x0+2*w//3+1)
        tops=[];bots=[]
        for cc in cols:
            ys=np.where(lab[:,cc]==k)[0]
            if len(ys): tops.append(ys.min()); bots.append(ys.max())
        rows.append((i,cen[k][0],cen[k][1],np.median(tops),np.median(bots),w,h))
    rows=np.array(rows)
    print('==',src)
    hc=121.65*(n@ray(583.0,434.5))  # tennis centre plane distance (anchor)
    P=[];C=[]
    for r in rows:
        i,u,v,t,b,w,h=r
        P.append(on_plane(u,(t+b)/2,hc)); C.append(capidx(int(i)))
    P=np.array(P); C=np.array(C)
    for k in range(len(P)-1):
        d=np.linalg.norm(P[k+1]-P[k])*25/(C[k+1]-C[k])
        print(' v%02d cap%02d->%02d u=%.1f vmid=%.1f  R=%.1f speed %.1f'%(rows[k,0],C[k],C[k+1],rows[k,1],(rows[k,3]+rows[k,4])/2,np.linalg.norm(P[k]),d))
