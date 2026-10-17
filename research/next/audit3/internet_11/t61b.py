import cv2,numpy as np
cap=cv2.VideoCapture('data/QuantiPhy/internet_0061.mp4')
fr=[]
while True:
    ok,im=cap.read()
    if not ok: break
    fr.append(im.astype(np.float32))
idx=list(range(40,62))+[62,66,70,75,80]
bg=np.median(np.stack([fr[i] for i in idx]),axis=0)
cv2.imwrite('research/next/audit3/internet_11/png/bg61.png',cv2.resize(bg.astype(np.uint8),None,fx=0.25,fy=0.25))
out=[]
for i in range(28,62):
    d=np.abs(fr[i]-bg).max(axis=2)
    m=(d>45).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((11,11),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    # choose component with largest area excluding those touching left border (hand)
    best=None
    for k in range(1,n):
        x,y,w,h,ar=st[k]
        if ar<2000: continue
        if x<=2: continue
        if best is None or ar>st[best][4]: best=k
    if best is None: print(i,'none'); continue
    x,y,w,h,ar=st[best]
    out.append((i,x,x+w,y,y+h,cen[best][0],cen[best][1],ar))
    print(i,'x %d-%d y %d-%d w %d h %d cx %.1f cy %.1f area %d'%(x,x+w,y,y+h,w,h,cen[best][0],cen[best][1],ar))
np.savetxt('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/t61.txt',np.array(out),fmt='%.1f')
