import cv2,numpy as np
c=cv2.VideoCapture('data/QuantiPhy/simulation_0124_segmented.mp4')
i=0
out=[]
while True:
    ok,im=c.read()
    if not ok: break
    f=im.astype(np.int16)
    d=(255-f).sum(2)
    m=(d>60).astype(np.uint8)
    nl,lab,st,cen=cv2.connectedComponentsWithStats(m)
    ks=[k for k in range(1,nl) if st[k][4]>200]
    desc=[]
    for k in ks:
        ys,xs=np.nonzero(lab==k)
        pts=np.stack([xs,ys],1).astype(np.float32)
        (cx,cy),(w,h),ang=cv2.minAreaRect(pts)
        mean=f[ys,xs].mean(0)
        desc.append((round(cen[k][0],2),round(cen[k][1],2),st[k][4],round(max(w,h),1),round(min(w,h),1),round(ang,1),tuple(int(x) for x in mean),st[k][:4].tolist()))
    print(i,desc)
    i+=1
