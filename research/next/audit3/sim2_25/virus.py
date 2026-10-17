import cv2,numpy as np,sys
v=sys.argv[1]
c=cv2.VideoCapture(v); f=0; res=[]
k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(71,71))
while True:
    ok,im=c.read()
    if not ok: break
    g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    m=(g<150).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,k)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    out=[]
    for i in range(1,n):
        if st[i,4]<3000: continue
        x,y,w,h=st[i,:4]
        touch = x<=0 or y<=0 or x+w>=g.shape[1] or y+h>=g.shape[0]
        cnts,_=cv2.findContours((lab==i).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        p=cnts[0][:,0,:].astype(float)
        # drop border points
        keep=(p[:,0]>1)&(p[:,1]>1)&(p[:,0]<g.shape[1]-2)&(p[:,1]<g.shape[0]-2)
        p=p[keep]
        A=np.c_[2*p[:,0],2*p[:,1],np.ones(len(p))]; b=(p**2).sum(1)
        sol=np.linalg.lstsq(A,b,rcond=None)[0]; cx,cy=sol[0],sol[1]; r=np.sqrt(sol[2]+cx*cx+cy*cy)
        out.append((cx,cy,r,st[i,4],touch))
    out.sort()
    res.append(out)
    if f%6==0 or f<3: print(f,[('%.1f %.1f r%.1f %s'%(o[0],o[1],o[2],'T' if o[4] else '')) for o in out])
    f+=1
import pickle; pickle.dump(res,open(sys.argv[2],'wb'))
