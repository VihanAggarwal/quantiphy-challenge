import cv2, numpy as np, sys
c=sys.argv[1]
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{c}.mp4')
f=0
while True:
    ok,im=cap.read()
    if not ok: break
    g=im.astype(int)
    m=((g.min(axis=2)<200)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
    comps=[(st[i,4],st[i,0],st[i,1],st[i,2],st[i,3],cen[i,0],cen[i,1]) for i in range(1,n) if st[i,4]>150]
    comps.sort(reverse=True)
    if f%6==0 or f==74:
        print(f, [(a,x,y,w,h,round(cx,1),round(cy,1)) for a,x,y,w,h,cx,cy in comps[:4]])
    f+=1
