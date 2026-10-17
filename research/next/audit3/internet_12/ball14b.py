import cv2, numpy as np
p='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0014.mp4'
cap=cv2.VideoCapture(p)
x0,y0,x1,y1=1340,480,1560,720
fr=[]
while True:
    ok,im=cap.read()
    if not ok: break
    fr.append(cv2.cvtColor(im[y0:y1,x0:x1],cv2.COLOR_BGR2GRAY).astype(np.float32))
fr=np.array(fr); bg=np.median(fr[::5],axis=0)
prev=np.array([1441.0-x0,588.0-y0]); pos={}
for i in range(190,262):
    db=cv2.GaussianBlur(fr[i]-bg,(5,5),1.2)
    yy,xx=np.mgrid[0:db.shape[0],0:db.shape[1]]
    m=(xx-prev[0])**2+(yy-prev[1])**2<8**2
    d2=np.where(m,db,-999); y,x=np.unravel_index(np.argmax(d2),d2.shape)
    w=d2[y-2:y+3,x-2:x+3].clip(0); gy,gx=np.mgrid[y-2:y+3,x-2:x+3]
    c=np.array([(w*gx).sum()/w.sum(),(w*gy).sum()/w.sum()]); pos[i]=c+[x0,y0]; prev=c
for i in range(190,262,5): print(i,'%.1f %.1f'%tuple(pos[i]))
for a,b in [(195,225),(200,220),(205,215),(180,240) if 180 in pos else (190,230)]:
    t=np.arange(a,b+1); P=np.array([pos[i] for i in t])
    v=np.hypot(np.polyfit(t,P[:,0],1)[0],np.polyfit(t,P[:,1],1)[0]); print(a,b,'px/fr %.3f'%v,'m/s@30 %.2f'%(v*30/12.79))
