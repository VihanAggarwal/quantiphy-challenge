import cv2, numpy as np, sys
vid = sys.argv[1]
out = sys.argv[2]
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
fr=np.array(fr)
N=len(fr)
bg=np.median(fr,axis=0).astype(np.uint8)
rows=[]
def fit_circle(x,y):
    A=np.c_[2*x,2*y,np.ones_like(x)]
    b=x**2+y**2
    sol,*_=np.linalg.lstsq(A,b,rcond=None)
    cx,cy=sol[0],sol[1]; r=np.sqrt(sol[2]+cx**2+cy**2)
    return cx,cy,r
for i in range(N):
    f=fr[i].astype(np.int16)
    d=(f-bg.astype(np.int16))
    # vacuum is white: brighter than bg and low saturation
    hsv=cv2.cvtColor(fr[i],cv2.COLOR_BGR2HSV)
    pos=(d.sum(2)>45)&(hsv[...,1]<40)&(hsv[...,2]>150)
    pos=pos.astype(np.uint8)
    pos=cv2.morphologyEx(pos,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(pos)
    if n<2: rows.append((i,np.nan,np.nan,np.nan,0,np.nan,np.nan)); continue
    k=1+np.argmax(st[1:,4])
    m=(lab==k).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
    # fill holes
    cnts,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    cnt=max(cnts,key=cv2.contourArea)
    mm=np.zeros_like(m); cv2.drawContours(mm,[cnt],-1,1,-1)
    M=cv2.moments(mm,True)
    cx,cy=M['m10']/M['m00'],M['m01']/M['m00']
    p=cnt[:,0,:].astype(float)
    fx,fy,fr_=fit_circle(p[:,0],p[:,1])
    # robust refit: drop points far from circle
    for _ in range(3):
        res=np.abs(np.hypot(p[:,0]-fx,p[:,1]-fy)-fr_)
        keep=res<max(2.0,2.5*np.median(res))
        fx,fy,fr_=fit_circle(p[keep,0],p[keep,1])
    x0,y0,w,h=cv2.boundingRect(cnt)
    rows.append((i,cx,cy,np.sqrt(M['m00']/np.pi)*2,M['m00'],fx,fy,fr_*2,w,h))
    print(i,'cent %.2f %.2f diamA %.1f | fit %.2f %.2f D %.1f | bbox %d %d'%(cx,cy,np.sqrt(M['m00']/np.pi)*2,fx,fy,fr_*2,w,h))
np.savetxt(out,np.array([r if len(r)==10 else r+(np.nan,)*3 for r in rows]),fmt='%.4f',delimiter=',',header='i,cx,cy,diamA,area,fx,fy,fitD,w,h')
