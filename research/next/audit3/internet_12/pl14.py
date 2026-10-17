import cv2, numpy as np
p='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0014.mp4'
cap=cv2.VideoCapture(p)
x0,y0,x1,y1=1340,480,1560,720
fr=[]
while True:
    ok,im=cap.read()
    if not ok: break
    fr.append(im[y0:y1,x0:x1].astype(np.float32))
fr=np.array(fr); bg=np.median(fr[::3],axis=0)
for i in [0,1,2,238,239,240,241,242,268,269,270,271,272]:
    d=np.abs(fr[i]-bg).sum(2)
    m=(d>60).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    out=sorted([(st[k,4],cen[k,0]+x0,cen[k,1]+y0) for k in range(1,n) if st[k,4]>=6],reverse=True)
    print(i,[('%d'%o[0],'%.1f'%o[1],'%.1f'%o[2]) for o in out[:4]])
