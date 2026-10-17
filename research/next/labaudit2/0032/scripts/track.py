# Track tennis (yellow) and white ball in all renders; centroid + bbox + edge-fit circle
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0032/scripts')
from common import *
out={}
for r in ['x','','s']:
    fr=frames(r); T={}
    for k,im in enumerate(fr):
        hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
        H,S,Vv=[hsv[...,i].astype(int) for i in range(3)]
        roi=np.zeros(Vv.shape,bool); roi[330:600,0:1280]=True
        yel=(H>=20)&(H<=45)&(S>100)&(Vv>100)&roi
        wht=(S<60)&(Vv>165)&roi
        res={}
        for name,m in [('yel',yel),('wht',wht)]:
            m8=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
            n,lab,st,cen=cv2.connectedComponentsWithStats(m8)
            if n<2: res[name]=None; continue
            kk=1+np.argmax(st[1:,4]); x,y,w,h,a=st[kk]
            if a<40: res[name]=None; continue
            comp=(lab==kk).astype(np.uint8)
            cnts,_=cv2.findContours(comp,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
            c=max(cnts,key=len)[:,0,:].astype(float)
            (ex,ey),er=cv2.minEnclosingCircle(c.astype(np.float32))
            # algebraic circle fit on contour
            A=np.c_[2*c[:,0],2*c[:,1],np.ones(len(c))]; bb=(c**2).sum(1)
            sol=np.linalg.lstsq(A,bb,rcond=None)[0]; fr_=np.sqrt(sol[2]+sol[0]**2+sol[1]**2)
            res[name]=dict(cx=float(cen[kk][0]),cy=float(cen[kk][1]),w=int(w),h=int(h),x0=int(x),y0=int(y),area=int(a),
                           fx=float(sol[0]),fy=float(sol[1]),fr=float(fr_))
        T[k]=res
    out[r or 'o']=T
json.dump(out,open(D+'track.json','w'))
for k in range(49):
    s='%2d c%2d '%(k,cap(k))
    for r in ['x','o','s']:
        for nm in ['yel','wht']:
            v=out[r][k][nm]
            s+=' %s%s:'%(r,nm[0])+('None' if v is None else '(%6.1f,%5.1f) %2dx%2d'%(v['cx'],v['cy'],v['w'],v['h']))
    print(s)
