import cv2, numpy as np, json
v='captured_0036'
F=[cv2.imread(f'frames/{v}/f{k:02d}.png') for k in range(49)]
bg=np.median(np.stack(F[40:49]),axis=0).astype(np.float32)
res={}
prev=None
for k in range(49):
    im=F[k].astype(np.float32)
    d=np.abs(im-bg).max(axis=2)
    hsv=cv2.cvtColor(F[k],cv2.COLOR_BGR2HSV)
    white=(hsv[...,2]>150)&(hsv[...,1]<60)
    m=((d>35)&white).astype(np.uint8)
    m[:,:]=m
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    best=None
    for i in range(1,n):
        x,y,w,h,a=st[i]
        if a<40: continue
        if y>650 and x>1000: continue
        sc=a
        if best is None or sc>best[0]: best=(a,i)
    if best is None: print(k,'none'); continue
    i=best[1]; x,y,w,h,a=st[i]
    cnt,_=cv2.findContours((lab==i).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cnt,key=len)
    (cx,cy),r=cv2.minEnclosingCircle(c)
    el=cv2.fitEllipse(c) if len(c)>=5 else None
    res[k]=dict(cx=float(cen[i][0]),cy=float(cen[i][1]),w=int(w),h=int(h),a=int(a),r=float(r),
                el=[float(el[0][0]),float(el[0][1]),float(min(el[1])),float(max(el[1])),float(el[2])] if el else None)
    print(k,'c=(%.1f,%.1f) w=%d h=%d a=%d eq_d=%.1f elminor=%.1f elmajor=%.1f'%(cen[i][0],cen[i][1],w,h,a,2*np.sqrt(a/np.pi),min(el[1]),max(el[1])))
json.dump(res,open('scripts/trk_o.json','w'))
