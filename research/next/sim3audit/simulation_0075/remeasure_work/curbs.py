from common import *
def bgimg(vid, step=3):
    V=load(vid); return np.median(V[::step].astype(np.float32),axis=0).astype(np.uint8)
def road_edge(ch, p0, p1, road_dir, half=25, step=3, thr_road=4.0, thr_side=10.0):
    """points where chroma rises from road (<thr_road) to curb (>thr_side) going away from road; returns list of xy"""
    p0=np.array(p0,float); p1=np.array(p1,float); d=(p1-p0); L=np.linalg.norm(d); d/=L; n=np.array([-d[1],d[0]])
    if n@np.array(road_dir,float)>0: n=-n   # n points from road to sidewalk
    pts=[]
    H,W=ch.shape
    for t in np.arange(0,L,step):
        c=p0+d*t; ss=np.arange(-half,half+0.01,0.25); xy=c[None,:]+ss[:,None]*n[None,:]
        if (xy[:,0]<0).any() or (xy[:,0]>W-1).any() or (xy[:,1]<0).any() or (xy[:,1]>H-1).any(): continue
        vals=cv2.remap(ch, xy[:,0].astype(np.float32).reshape(1,-1), xy[:,1].astype(np.float32).reshape(1,-1), cv2.INTER_LINEAR).ravel()
        # road side at start (negative s); find first crossing of mid level going +s
        if np.median(vals[:15])>thr_road or np.median(vals[-15:])<thr_side: continue
        lvl=(np.median(vals[:15])+min(np.max(vals),np.median(vals[-15:])+10))/2
        lvl=max(lvl,6.0)
        idx=np.where(vals>lvl)[0]
        if len(idx)==0: continue
        j=idx[0]
        sj=ss[j-1]+(lvl-vals[j-1])/(vals[j]-vals[j-1])*(ss[j]-ss[j-1])
        pts.append(c+sj*n)
    return np.array(pts)
def robust_line(P,it=4,tol=1.5):
    keep=np.ones(len(P),bool)
    for _ in range(it):
        ln,_=fitline(P[keep]); r=P@ln[:2]+ln[2]; keep=np.abs(r)<max(tol,2.5*np.std(r[keep]))
    ln,res=fitline(P[keep]); return ln, res.std(), int(keep.sum())
def inter(l1,l2):
    p=np.cross(l1,l2); return p[:2]/p[2]
