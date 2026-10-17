import cv2, numpy as np, sys
c=sys.argv[1]; thr=int(sys.argv[2])
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{c}.mp4')
W=[];f=0
while True:
    ok,im=cap.read()
    if not ok: break
    m=(im.astype(int).min(axis=2)<thr).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    # exclude rabbit: zero out components with area<6000 touching y>1450
    n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
    for i in range(1,n):
        if st[i,4]<6000: m[lab==i]=0
    up=m[1120:1330]; lo=m[1375:1560]
    cu=np.where(up.sum(0)>1)[0]; cl=np.where(lo.sum(0)>1)[0]
    right=cu.max(); left=cl.min()
    # top of antelope: topmost row with pixels in columns > 500 or right-of-tree
    W.append((f,left,right,right-left)); f+=1
W=np.array(W)
print(c,'width median',np.median(W[:,3]),'mean',W[:,3].mean().round(1),'p10/p90',np.percentile(W[:,3],[10,90]))
print('w every 6',W[::6,3])
print('left every 6',W[::6,1])
