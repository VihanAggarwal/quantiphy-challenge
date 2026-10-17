import cv2, numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0215.mp4')
ok,f=c.read()
g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
def fit_circle(xs,ys):
    A=np.c_[2*xs,2*ys,np.ones(len(xs))]; b=xs**2+ys**2
    cx,cy,k=np.linalg.lstsq(A,b,rcond=None)[0]; r=np.sqrt(k+cx**2+cy**2); return cx,cy,r
for name,(x0,x1,y0,y1),thr in [('lampshade',(1090,1320,120,320),150),('vase',(700,810,180,290),150)]:
    sub=g[y0:y1,x0:x1]
    m=(sub>thr).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); mk=(lab==k).astype(np.uint8)
    # fill holes
    cnts,_=cv2.findContours(mk,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    cnt=max(cnts,key=cv2.contourArea)[:,0,:].astype(float)
    cx,cy,r=fit_circle(cnt[:,0],cnt[:,1])
    (ex,ey),er=cv2.minEnclosingCircle(cnt.astype(np.float32))
    xs=cnt[:,0]; ys=cnt[:,1]
    print(name,'fit centre (%.1f,%.1f) r %.1f | encl (%.1f,%.1f) r %.1f | bbox x %.0f-%.0f y %.0f-%.0f | area-equiv r %.1f'%(
        cx+x0,cy+y0,r,ex+x0,ey+y0,er,xs.min()+x0,xs.max()+x0,ys.min()+y0,ys.max()+y0,np.sqrt(cv2.contourArea(cnt.astype(np.float32))/np.pi)))
# dark inner opening of lampshade & vase (dark hole)
for name,(x0,x1,y0,y1),thr in [('lamp opening',(1150,1250,170,260),90),('vase hole',(730,780,205,250),60)]:
    sub=g[y0:y1,x0:x1]; m=(sub<thr).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); ys,xs=np.nonzero(lab==k)
    print(name,'centroid (%.1f,%.1f) bbox x %d-%d y %d-%d'%(xs.mean()+x0,ys.mean()+y0,xs.min()+x0,xs.max()+x0,ys.min()+y0,ys.max()+y0))
