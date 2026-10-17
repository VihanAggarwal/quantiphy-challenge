import cv2,numpy as np
cap=cv2.VideoCapture('data/QuantiPhy/internet_0045.mp4')
fr=[]
while True:
    ok,im=cap.read()
    if not ok: break
    fr.append(im)
bg=fr[44].astype(np.float32)
for i in range(4,32):
    f=fr[i]
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    d=np.abs(f.astype(np.float32)-bg).max(axis=2)
    m=((hsv[:,:,1]<50)&(hsv[:,:,2]>175)&(d>25)).astype(np.uint8)
    m[:500]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    k=1+np.argmax(st[1:,4]); x,y,w,h,ar=st[k]
    mm=(lab==k)
    cols=np.where(mm.any(axis=0))[0]
    ext=[]
    for c in cols:
        ys=np.where(mm[:,c])[0]; ext.append((ys[-1]-ys[0]+1,ys[0],ys[-1]))
    ext=np.array(ext)
    j=np.argsort(ext[:,0])[-max(3,len(ext)//20):]
    print(i,'bbox x %d-%d y %d-%d'%(x,x+w,y,y+h),'max col extent',int(ext[:,0].max()),'p95 ext',int(np.median(ext[j,0])),'top',int(np.median(ext[j,1])),'bot',int(np.median(ext[j,2])),'cx %.1f'%cen[k][0])
