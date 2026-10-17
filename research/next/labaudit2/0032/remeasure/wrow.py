import cv2,numpy as np,json
def fit_circle(pts):
    x,y=pts[:,0],pts[:,1]
    M=np.c_[x,y,np.ones(len(x))]
    p,*_=np.linalg.lstsq(M,-(x*x+y*y),rcond=None)
    x0=-p[0]/2;y0=-p[1]/2;r=np.sqrt(x0*x0+y0*y0-p[2]); return x0,y0,r
def measure(img,xc,yc,R,frac=0.75,ch='L',sub=0.25):
    lab=cv2.cvtColor(img,cv2.COLOR_BGR2LAB).astype(np.float32)
    g=lab[...,0] if ch=='L' else cv2.cvtColor(img,cv2.COLOR_BGR2GRAY).astype(np.float32)
    for it in range(4):
        pts=[]
        for y in np.arange(yc-frac*R,yc+frac*R+1e-6,sub):
            xs=np.arange(xc-R-12,xc+R+12,0.1)
            pr=cv2.remap(g,np.float32(xs).reshape(1,-1),np.float32(np.full_like(xs,y)).reshape(1,-1),cv2.INTER_LINEAR).ravel()
            chord=np.sqrt(max(R*R-(y-yc)**2,1))
            inside=np.percentile(pr[np.abs(xs-xc)<0.5*chord],60)
            oL=np.median(pr[(xs<xc-R-5)&(xs>xc-R-11)]); oR=np.median(pr[(xs>xc+R+5)&(xs<xc+R+11)])
            for o,side in [(oL,-1),(oR,1)]:
                if inside-o<30: continue
                thr=(inside+o)/2
                if side==1:
                    idx=np.where((xs>xc)&(pr<thr))[0]
                    if len(idx)==0: continue
                    k=idx[0]; xe=xs[k-1]+(pr[k-1]-thr)/(pr[k-1]-pr[k])*0.1
                else:
                    idx=np.where((xs<xc)&(pr<thr))[0]
                    if len(idx)==0: continue
                    k=idx[-1]; xe=xs[k+1]-(pr[k+1]-thr)/(pr[k+1]-pr[k])*0.1
                pts.append((xe,y))
        pts=np.array(pts)
        xc,yc,R=fit_circle(pts)
    res=np.hypot(pts[:,0]-xc,pts[:,1]-yc)-R
    return xc,yc,R,len(pts),res.std()
if __name__=='__main__':
    W=json.load(open('wrad.json'))
    out={}
    for i in range(36,49):
        img=cv2.imread('frames/f%02d.png'%i)
        x0,y0,r0=W[str(i)][0][:3]
        rows=[]
        for frac in [0.6,0.75,0.85]:
            rows.append(measure(img,x0,y0,r0,frac=frac))
        out[i]=rows
        print(i,' | '.join('c=(%.2f,%.2f) d=%.2f n=%d rms=%.2f'%(r[0],r[1],2*r[2],r[3],r[4]) for r in rows))
    json.dump(out,open('wrow.json','w'))
