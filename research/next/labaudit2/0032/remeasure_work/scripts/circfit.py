import numpy as np, sys, cv2
def map_coordinates(img,coords,order=1):
    ys,xs=coords
    x0=np.floor(xs).astype(int); y0=np.floor(ys).astype(int)
    fx=xs-x0; fy=ys-y0
    a=img[y0,x0]; b=img[y0,x0+1]; c=img[y0+1,x0]; d=img[y0+1,x0+1]
    return a*(1-fx)*(1-fy)+b*fx*(1-fy)+c*(1-fx)*fy+d*fx*fy
src=sys.argv[1]; tag=sys.argv[2]
cap=cv2.VideoCapture(src); fr=[]
while True:
    ok,img=cap.read()
    if not ok: break
    fr.append(img)
def blob(img):
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV).astype(int)
    roi=np.zeros(hsv.shape[:2],bool); roi[380:520,450:1000]=True
    m=((hsv[...,1]<60)&(hsv[...,2]>170)&roi).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n_,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); return cen[k]
out=[]
for i in range(32,49):
    img=fr[i]
    cx,cy=blob(img)
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV).astype(float)
    Wm=(hsv[...,2]/255.0)*(1-hsv[...,1]/255.0)
    Wm=cv2.GaussianBlur(Wm,(0,0),0.7)
    for it in range(3):
        pts=[]
        for th in np.radians(np.arange(-25,206,5)):
            dx,dy=np.cos(th),-np.sin(th)
            s=np.arange(0,22,0.25)
            xs=cx+dx*s; ys=cy+dy*s
            p=map_coordinates(Wm,[ys,xs],order=1)
            inner=p[:8].mean(); outer=p[-12:].mean()
            if inner-outer<0.2: continue
            t=(inner+outer)/2
            k=np.where(p<t)[0]
            k=k[k>4]
            if len(k)==0: continue
            k=k[0]
            sub=s[k-1]+(p[k-1]-t)/(p[k-1]-p[k])*0.25
            pts.append((cx+dx*sub, cy+dy*sub))
        P=np.array(pts)
        A=np.c_[2*P[:,0],2*P[:,1],np.ones(len(P))]; b=(P**2).sum(1)
        sol,_,_,_=np.linalg.lstsq(A,b,rcond=None)
        xc,yc=sol[0],sol[1]; r=np.sqrt(sol[2]+xc**2+yc**2)
        res=np.sqrt(((P-[xc,yc])**2).sum(1))-r
        # reject outliers and refit
        good=np.abs(res)<2*np.std(res)+0.3
        P=P[good]
        A=np.c_[2*P[:,0],2*P[:,1],np.ones(len(P))]; b=(P**2).sum(1)
        sol,_,_,_=np.linalg.lstsq(A,b,rcond=None)
        xc,yc=sol[0],sol[1]; r=np.sqrt(sol[2]+xc**2+yc**2)
        res=np.sqrt(((P-[xc,yc])**2).sum(1))-r
        cx,cy=xc,yc
    out.append((i,xc,yc,r,len(P),res.std()))
    print('%s f%02d centre (%.2f, %.2f) r=%.2f n=%d rms=%.2f   top=%.2f'%(tag,i,xc,yc,r,len(P),res.std(),yc-r))
np.save('/home/user/quantiphy-challenge/research/next/labaudit2/0032/remeasure_work/circ_%s.npy'%tag,np.array(out))
