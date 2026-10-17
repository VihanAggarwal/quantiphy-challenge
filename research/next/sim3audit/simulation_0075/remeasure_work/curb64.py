from common import *
s=np.load('std64.npy').astype(np.float32)
s=cv2.GaussianBlur(s,(5,5),0)
def tex_edge(p0,p1,road_side,half=30,step=4):
    p0=np.array(p0,float); p1=np.array(p1,float); d=(p1-p0); L=np.linalg.norm(d); d/=L; n=np.array([-d[1],d[0]])
    if n@np.array(road_side)<0: n=-n
    pts=[]
    for t in np.arange(0,L,step):
        c=p0+d*t; ss=np.arange(-half,half+0.01,0.5); xy=c[None,:]+ss[:,None]*n[None,:]
        if (xy<0).any() or (xy[:,0]>2159).any() or (xy[:,1]>1079).any(): continue
        vals=cv2.remap(s, xy[:,0].astype(np.float32).reshape(1,-1), xy[:,1].astype(np.float32).reshape(1,-1), cv2.INTER_LINEAR).ravel()
        lo=np.median(vals[:20]); hi=np.median(vals[-20:])
        if hi-lo<4: continue
        lvl=(lo+hi)/2
        # first crossing from road side going inward: last index (from start) where below lvl before staying above
        above=vals>lvl
        # find first index j such that all of above[j:j+10] true
        j=None
        for k in range(len(vals)-10):
            if above[k:k+10].all(): j=k; break
        if j is None or j==0: continue
        sj=ss[j-1]+(lvl-vals[j-1])/(vals[j]-vals[j-1])*(ss[j]-ss[j-1])
        pts.append(c+sj*n)
    return np.array(pts)
def robust_line(P,it=3,tol=2.0):
    keep=np.ones(len(P),bool)
    for _ in range(it):
        ln,res=fitline(P[keep]); r=P@ln[:2]+ln[2]; keep=np.abs(r)<max(tol,2.5*np.std(r[keep]))
    ln,res=fitline(P[keep]); return ln, res.std(), keep.sum()
if __name__=='__main__':
    segs={'NL':((610,575),(310,1070),(1,0)),'NR':((1810,560),(2150,890),(-1,0)),
          'FL':((985,40),(860,280),(1,0)),'FR':((1255,40),(1500,290),(-1,0))}
    out={}
    for k,(a,b,rs) in segs.items():
        P=tex_edge(a,b,rs); ln,rms,n=robust_line(P); out[k]=ln
        print(k,n,len(P),'rms %.2f'%rms, ln)
    vp1=np.cross(out['NL'],out['NR']); vp1=vp1[:2]/vp1[2]
    vp2=np.cross(out['FL'],out['FR']); vp2=vp2[:2]/vp2[2]
    print('VP near',vp1,'VP far',vp2)
    np.save('lines64.npy',out)
