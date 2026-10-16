import cv2, numpy as np, json
D='/home/user/quantiphy-challenge/research/next/labaudit/0031/'
tr=json.load(open(D+'track.json'))
def fit_circle(pts):
    P=np.array(pts,float); A=np.c_[2*P,np.ones(len(P))]; b=(P**2).sum(1)
    s,*_=np.linalg.lstsq(A,b,rcond=None); xc,yc=s[:2]; r=np.sqrt(s[2]+xc**2+yc**2); return xc,yc,r
out={}
for r in ['0','x']:
    out[r]={}
    for key,angs in [('W',np.deg2rad(np.arange(-180,1,10))),('T',np.deg2rad(np.arange(-180,1,10)))]:
        res=[]
        for i in range(0,47):
            t=tr[r][key][i]
            if t[1] is None: res.append(None); continue
            f=cv2.imread(D+f'frames/r{r}_{i:02d}.png')
            g=cv2.GaussianBlur(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(float),(3,3),0.8)
            gx=cv2.Sobel(g,cv2.CV_64F,1,0,ksize=3); gy=cv2.Sobel(g,cv2.CV_64F,0,1,ksize=3)
            xc,yc=t[1],t[2]; r0=t[6]/2
            pts=[]
            for it in range(2):
                pts=[]
                for a in angs:
                    dx,dy=np.cos(a),np.sin(a)
                    rs=np.arange(0.5*r0,1.6*r0,0.25)
                    xs=xc+rs*dx; ys=yc+rs*dy
                    gr=cv2.remap(gx.astype(np.float32),xs.astype(np.float32).reshape(1,-1),ys.astype(np.float32).reshape(1,-1),cv2.INTER_LINEAR)[0]*dx+\
                       cv2.remap(gy.astype(np.float32),xs.astype(np.float32).reshape(1,-1),ys.astype(np.float32).reshape(1,-1),cv2.INTER_LINEAR)[0]*dy
                    gr=np.abs(gr)
                    k=np.argmax(gr); pts.append((xs[k],ys[k]))
                pts=np.array(pts)
                xc2,yc2,rr=fit_circle(pts)
                d=np.hypot(pts[:,0]-xc2,pts[:,1]-yc2)
                keep=np.abs(d-rr)<max(1.0,0.12*rr)
                if keep.sum()>6: xc2,yc2,rr=fit_circle(pts[keep])
                xc,yc,r0=xc2,yc2,rr
            res.append([i,float(xc),float(yc),float(2*r0)])
        out[r][key]=res
        print(r,key,' '.join('%d:%.1f'%(q[0],q[3]) for q in res if q and q[0]%2==0))
json.dump(out,open(D+'circ.json','w'))
