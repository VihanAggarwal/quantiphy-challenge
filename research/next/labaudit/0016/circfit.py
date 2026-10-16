import cv2,numpy as np,sys
f=711.;cx,cy=640,360
def fit(i,rend,box,thr=185):
    im=cv2.imread('frames/f%s_%02d.png'%(rend,i))
    x0,y0,x1,y1=box
    c=im[y0:y1,x0:x1]
    hsv=cv2.cvtColor(c,cv2.COLOR_BGR2HSV)
    white=((hsv[...,2]>thr)&(hsv[...,1]<40)).astype(np.uint8)
    # fill black patches: close
    k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(15,15))
    m=cv2.morphologyEx(white,cv2.MORPH_CLOSE,k)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
    kk=1+np.argmax(st[1:,4]); m=(lab==kk).astype(np.uint8)
    cnts,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    cnt=max(cnts,key=len)[:,0,:].astype(float)
    (ex,ey),(MA,ma),ang=cv2.fitEllipse(cnt.astype(np.float32))
    # algebraic circle fit
    A=np.c_[2*cnt[:,0],2*cnt[:,1],np.ones(len(cnt))]; b=(cnt**2).sum(1)
    sol=np.linalg.lstsq(A,b,rcond=None)[0]; r=np.sqrt(sol[2]+sol[0]**2+sol[1]**2)
    x,y,w,h=cv2.boundingRect(m)
    cv2.imwrite('mask_%s%02d.png'%(rend,i),m*255)
    return dict(i=i,bbox=(x+x0,y+y0,w,h),circ=(round(sol[0]+x0,1),round(sol[1]+y0,1),round(2*r,1)),ell=(round(ex+x0,1),round(ey+y0,1),round(MA,1),round(ma,1),round(ang)))
for rend in ['o','s']:
    for i in [16,20,22,24]:
        print(rend,fit(i,rend,(200,500,420,720)))
