import cv2, numpy as np
def bilinear(img,ys,xs):
    x0=np.floor(xs).astype(int); y0=np.floor(ys).astype(int); dx=xs-x0; dy=ys-y0
    return (img[y0,x0]*(1-dx)*(1-dy)+img[y0,x0+1]*dx*(1-dy)+img[y0+1,x0]*(1-dx)*dy+img[y0+1,x0+1]*dx*dy)
def kasa(pts):
    x,y=pts[:,0],pts[:,1]
    A=np.c_[2*x,2*y,np.ones_like(x)]; b=x**2+y**2
    (cx,cy,c),*_=np.linalg.lstsq(A,b,rcond=None)
    r=np.sqrt(c+cx**2+cy**2); res=np.hypot(x-cx,y-cy)-r
    return cx,cy,r,np.std(res)
def fit(i, lvl_frac=0.5, angs=None, c0=(616.5,280.5)):
    f=cv2.imread(f'frames/f{i:02d}.png').astype(float)
    sig=f[...,2]-f[...,1]
    bg=np.median(sig[245:258,590:645])
    cxi,cyi=int(c0[0]),int(c0[1])
    ball=np.median(sig[cyi-7:cyi+7,cxi-8:cxi+8])
    lvl=bg+lvl_frac*(ball-bg)
    c0=np.array(c0,float)
    pts=[]
    if angs is None: angs=np.r_[np.arange(-180,1,6), np.arange(6,31,6), np.arange(150,175,6)]
    for a in np.radians(angs):
        rr=np.arange(4,20,0.1)
        xs=c0[0]+rr*np.cos(a); ys=c0[1]+rr*np.sin(a)
        v=bilinear(sig,ys,xs)
        k=np.nonzero(v<lvl)[0]
        if len(k)==0 or k[0]==0: continue
        k=k[0]; r=rr[k-1]+(v[k-1]-lvl)/(v[k-1]-v[k])*0.1
        pts.append((c0[0]+r*np.cos(a),c0[1]+r*np.sin(a)))
    pts=np.array(pts)
    return kasa(pts),len(pts)
if __name__=='__main__':
    for i in [0,4,8,12,16,20,24]:
        for fr in [0.3,0.5,0.7]:
            (x,y,r,s),n=fit(i,fr)
            print(i,fr,'centre (%.1f,%.1f) diam %.2f px  resid %.2f n %d'%(x,y,2*r,s,n))
