import cv2, numpy as np
VD='/home/user/quantiphy-challenge/data/QuantiPhy/'
def load(vid):
    cap=cv2.VideoCapture(VD+vid+'.mp4'); fr=[]
    while True:
        ok,f=cap.read()
        if not ok: break
        fr.append(f)
    return np.array(fr)
def chroma(img):
    f=img.astype(np.float32); return f[...,2]-f[...,0]   # R-B
def fitline(pts):
    pts=np.asarray(pts,float); m=pts.mean(0); u,s,vt=np.linalg.svd(pts-m); d=vt[0]
    n=np.array([-d[1],d[0]]); c=-n@m
    res=(pts@n+c)
    return np.array([n[0],n[1],c]), res
def edge_profile(img, p0, p1, half=25, step=4, side_from=+1, thr=None):
    """sample along segment p0->p1; at each point, take a perpendicular profile of chroma; return points of max |gradient|"""
    p0=np.array(p0,float); p1=np.array(p1,float); d=(p1-p0); L=np.linalg.norm(d); d/=L; n=np.array([-d[1],d[0]])
    ch=cv2.GaussianBlur(chroma(img),(3,3),0)
    out=[]
    for t in np.arange(0,L,step):
        c=p0+d*t
        ss=np.arange(-half,half+0.01,0.5)
        xy=c[None,:]+ss[:,None]*n[None,:]
        vals=cv2.remap(ch, xy[:,0].astype(np.float32).reshape(1,-1), xy[:,1].astype(np.float32).reshape(1,-1), cv2.INTER_LINEAR).ravel()
        g=np.gradient(vals)
        k=np.argmax(np.abs(g)*(1 if side_from==0 else 1))
        out.append((c+ss[k]*n, vals, g[k]))
    return out
