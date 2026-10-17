import cv2,numpy as np,json,sys
def samp(g,xs,ys):
    return cv2.remap(g,np.float32(xs).reshape(1,-1),np.float32(ys).reshape(1,-1),cv2.INTER_LINEAR).ravel()
def fit_circle(pts):
    x,y=pts[:,0],pts[:,1]
    M=np.c_[x,y,np.ones(len(x))]
    p,*_=np.linalg.lstsq(M,-(x*x+y*y),rcond=None)
    x0=-p[0]/2;y0=-p[1]/2;r=np.sqrt(x0*x0+y0*y0-p[2]); return x0,y0,r
def measure(img,x0,y0,r0,excl=(50,130),step=6,verbose=False):
    g=cv2.cvtColor(img,cv2.COLOR_BGR2LAB)[...,0].astype(np.float32)
    g=cv2.GaussianBlur(g,(0,0),0.7)
    for it in range(4):
        pts=[];angs=[]
        for a in np.arange(0,360,step):
            if excl[0]<a<excl[1]: continue
            t=np.deg2rad(a)
            rr=np.arange(0,r0+12,0.2)
            pr=samp(g,x0+rr*np.cos(t),y0+rr*np.sin(t))
            inner=np.percentile(pr[(rr>0.3*r0)&(rr<0.7*r0)],50)
            outer=np.median(pr[(rr>r0+5)&(rr<r0+10)])
            if inner-outer<25: continue
            thr=(inner+outer)/2
            # first crossing outward beyond 0.5 r0
            idx=np.where((rr>0.5*r0)&(pr<thr))[0]
            if len(idx)==0: continue
            k=idx[0]
            rcross=rr[k-1]+(pr[k-1]-thr)/(pr[k-1]-pr[k])*0.2
            pts.append((x0+rcross*np.cos(t),y0+rcross*np.sin(t))); angs.append(a)
        pts=np.array(pts)
        if len(pts)<8: return None
        x0,y0,r0=fit_circle(pts)
    res=np.hypot(pts[:,0]-x0,pts[:,1]-y0)-r0
    return x0,y0,r0,len(pts),res.std()
if __name__=='__main__':
    T=json.load(open('track_color.json'))
    S={r['i']:r for r in json.load(open('wsize.json'))}
    out={}
    for i in range(33,49):
        img=cv2.imread('frames/f%02d.png'%i)
        x0,y0=(S[i]['cx'],S[i]['cy'])
        rows=[]
        for excl in [(50,130),(30,150),(-1,-1)]:
            r=measure(img,x0,y0,11,excl=excl)
            rows.append(r)
        out[i]=rows
        print(i,' | '.join('c=(%.2f,%.2f) d=%.2f n=%d rms=%.2f'%(r[0],r[1],2*r[2],r[3],r[4]) if r else 'None' for r in rows))
    json.dump(out,open('wrad.json','w'))
