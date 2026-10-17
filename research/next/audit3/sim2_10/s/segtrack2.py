import cv2, numpy as np, sys, csv
# per-frame: antelope = largest comp with bottom>ybot ; rabbit = comp with area in [amin,amax]
c=sys.argv[1]; thr=int(sys.argv[2]); ybot=int(sys.argv[3]); rmin,rmax=[int(v) for v in sys.argv[4].split(',')]
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{c}.mp4')
rows=[]; f=0
while True:
    ok,im=cap.read()
    if not ok: break
    g=im.astype(int)
    m=((g.min(axis=2)<thr)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
    A=None;R=None
    for i in range(1,n):
        x,y,w,h,a=st[i]
        if y+h>ybot and a>20000 and (A is None or a>A[4]): A=(x,y,w,h,a,cen[i,0],cen[i,1])
        if rmin<=a<=rmax and y+h>ybot-40 and (R is None or a>R[4]): R=(x,y,w,h,a,cen[i,0],cen[i,1])
    r=[f]+(list(A) if A else [np.nan]*7)+(list(R) if R else [np.nan]*7)
    rows.append(r); f+=1
a=np.array(rows,float)
np.savetxt(f'/home/user/quantiphy-challenge/research/next/audit3/sim2_10/{c}_t{thr}.csv',a,delimiter=',',fmt='%.2f',header='f,ax,ay,aw,ah,aa,acx,acy,rx,ry,rw,rh,ra,rcx,rcy')
fr=a[:,0]
for k,nm in [(3,'aw'),(4,'ah'),(10,'rw'),(11,'rh')]:
    v=a[:,k]; v=v[~np.isnan(v)]
    print(nm,'n',len(v),'median',np.median(v),'mean',v.mean().round(1),'min',v.min(),'max',v.max(),'p10,p90',np.percentile(v,[10,90]))
for k,nm in [(6,'acx'),(13,'rcx'),(1,'ax_left'),(15-12,'')]:
    if not nm: continue
    v=a[:,k]; ok=~np.isnan(v)
    p=np.polyfit(fr[ok],v[ok],1); print(nm,'slope px/f',p[0].round(3),'n',ok.sum())
# right edge (nose) slope
v=a[:,1]+a[:,3]; ok=~np.isnan(v); print('a_right slope',np.polyfit(fr[ok],v[ok],1)[0].round(3))
v=a[:,8]+a[:,10]; ok=~np.isnan(v); print('r_right slope',np.polyfit(fr[ok],v[ok],1)[0].round(3))
