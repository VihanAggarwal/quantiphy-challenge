import cv2, numpy as np, sys
c=sys.argv[1]; x0,x1,y0,y1=map(int,sys.argv[2:6]); thr=int(sys.argv[6]) if len(sys.argv)>6 else 45
cap=cv2.VideoCapture(f'data/QuantiPhy/{c}.mp4')
F=[]
while True:
    ok,f=cap.read()
    if not ok: break
    F.append(f[y0:y1,x0:x1].copy())
F=np.array(F)
bg=np.median(F,axis=0)
res=[]
for i in range(len(F)):
    d=np.abs(F[i].astype(float)-bg).sum(2)
    g=cv2.cvtColor(F[i],cv2.COLOR_BGR2GRAY)
    m=((d>thr)&(g>45)).astype(np.uint8)   # exclude black cat
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    j=1+np.argmax(st[1:,4]); x,y,w,h,a=st[j]
    xs=[x,x+w]; ys=[y,y+h]
    for k in range(1,n):
        if k==j or st[k,4]<40: continue
        X,Y,Wd,H,A=st[k]
        if X<x+w+25 and X+Wd>x-25 and Y<y+h+25 and Y+H>y-25:
            xs+=[X,X+Wd]; ys+=[Y,Y+H]
    res.append((i,x0+min(xs),x0+max(xs),y0+min(ys),y0+max(ys),a))
for r in res[::3]: print('f%d x %d-%d (%d) y %d-%d (%d) area %d'%(r[0],r[1],r[2],r[2]-r[1],r[3],r[4],r[4]-r[3],r[5]))
w=np.array([r[2]-r[1] for r in res]); h=np.array([r[4]-r[3] for r in res])
print('width median %d p10 %d p90 %d max %d ; height median %d p10 %d p90 %d max %d'%(np.median(w),np.percentile(w,10),np.percentile(w,90),w.max(),np.median(h),np.percentile(h,10),np.percentile(h,90),h.max()))
