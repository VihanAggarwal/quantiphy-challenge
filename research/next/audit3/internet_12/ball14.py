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
pos={}
for i in range(150,287):
    d=fr[i]-bg
    # ball: small bright blob; use gaussian blur & find max excluding penalty spot
    db=cv2.GaussianBlur(d,(5,5),1.2)
    db[(np.arange(db.shape[0])[:,None]-41)**2+(np.arange(db.shape[1])[None,:]-110)**2<100]=-999
    yy,xx=np.unravel_index(np.argmax(db),db.shape)
    # centroid refine
    w=db[max(yy-3,0):yy+4,max(xx-3,0):xx+4].clip(0)
    gy,gx=np.mgrid[max(yy-3,0):yy+4,max(xx-3,0):xx+4]
    cx=(w*gx).sum()/w.sum()+x0; cy=(w*gy).sum()/w.sum()+y0
    pos[i]=(cx,cy,db[yy,xx])
for i in range(150,287,5): print(i,'%.1f %.1f %.0f'%pos[i])
P=np.array([pos[i][:2] for i in range(195,226)]); t=np.arange(195,226)
vx=np.polyfit(t,P[:,0],1)[0]; vy=np.polyfit(t,P[:,1],1)[0]
v=np.hypot(vx,vy); print('ball 195-225 px/frame',v,'m/s @30fps',v*30/12.79, '@29.76',v*29.764/12.79)
P=np.array([pos[i][:2] for i in range(200,221)]); t=np.arange(200,221)
v=np.hypot(np.polyfit(t,P[:,0],1)[0],np.polyfit(t,P[:,1],1)[0]); print('ball 200-220',v*30/12.79)
