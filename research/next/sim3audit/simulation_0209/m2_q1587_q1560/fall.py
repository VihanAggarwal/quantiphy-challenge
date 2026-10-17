import cv2,numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0209.mp4')
F=[]
while True:
    ok,f=cap.read()
    if not ok: break
    F.append(f.astype(np.float32))
bg=F[29]
res=[]
for i in range(0,12):
    d=np.abs(F[i]-bg).sum(2)
    m=(d>60).astype(np.uint8)
    m[640:,:]=0  # ignore desk region below
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,cv2.CC_STAT_AREA])
    x,y,w,h,a=st[k]
    ys,xs=np.nonzero(lab==k)
    # bottom edge: median of lowest rows per column within central 60% columns
    res.append((i,x,y,w,h,a,cen[k][0],cen[k][1]))
    print(i,x,y,w,h,a,round(cen[k][0],2),round(cen[k][1],2))
np.save('fall_track.npy',np.array(res))
