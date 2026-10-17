import cv2, numpy as np, sys
from common import *
vid=sys.argv[1] if len(sys.argv)>1 else 'simulation_0062'
img=cv2.imread(f'fr/{vid}_000.png')
ch=cv2.GaussianBlur(chroma(img),(3,3),0)
def curb_edge(p0,p1,half=20,step=3,mode='road'):
    p0=np.array(p0,float); p1=np.array(p1,float); d=(p1-p0); L=np.linalg.norm(d); d/=L; n=np.array([-d[1],d[0]])
    if n[1]<0: n=-n   # point downward (assume road below)
    pts=[]
    for t in np.arange(0,L,step):
        c=p0+d*t; ss=np.arange(-half,half+0.01,0.25); xy=c[None,:]+ss[:,None]*n[None,:]
        vals=cv2.remap(ch, xy[:,0].astype(np.float32).reshape(1,-1), xy[:,1].astype(np.float32).reshape(1,-1), cv2.INTER_LINEAR).ravel()
        if vals.max()<25: continue
        # band: peak; road-side edge: first crossing below half-peak after peak
        k=np.argmax(vals); pk=vals[k]; base=np.median(vals[-20:])
        lvl=(pk+base)/2
        j=k
        while j<len(vals)-1 and vals[j]>lvl: j+=1
        if j>=len(vals)-1: continue
        # subpixel
        s=ss[j-1]+(vals[j-1]-lvl)/(vals[j-1]-vals[j])*(ss[j]-ss[j-1])
        # sidewalk-side edge of band (top of curb face) too
        i=k
        while i>0 and vals[i]>lvl: i-=1
        s2=ss[i]+(lvl-vals[i])/(vals[i+1]-vals[i])*(ss[i+1]-ss[i]) if i>0 else np.nan
        pts.append((*(c+s*n), *(c+s2*n), pk))
    return np.array(pts)
if __name__=='__main__':
    for name,(p0,p1) in {'L':((5,808),(670,638)),'R':((1870,637),(2155,669))}.items():
        P=curb_edge(p0,p1)
        ln,res=fitline(P[:,:2]); ln2,res2=fitline(P[:,2:4][~np.isnan(P[:,2])])
        print(name, len(P), 'base line',ln, 'rms',res.std(), 'top line', ln2, 'rms', res2.std(), 'peak', np.median(P[:,4]))
        a,b,c=ln; print('  du/dv =', -b/a, ' slope dv/du', -a/b)
