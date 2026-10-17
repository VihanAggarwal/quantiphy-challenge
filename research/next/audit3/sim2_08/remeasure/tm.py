from util import *
import sys
def subpix(r):
    _,mx,_,(x,y)=cv2.minMaxLoc(r)
    dy=dx=0.
    if 0<y<r.shape[0]-1:
        a,b,c=r[y-1,x],r[y,x],r[y+1,x]; dy=0.5*(a-c)/(a-2*b+c)
    if 0<x<r.shape[1]-1:
        a,b,c=r[y,x-1],r[y,x],r[y,x+1]; dx=0.5*(a-c)/(a-2*b+c)
    return x+dx,y+dy,mx
def track(v,tf,box,x0,x1,frs):
    F=frames(v)
    bx0,bx1,by0,by1=box
    T=F[tf][by0:by1,bx0:bx1]
    res=[]
    for i in frs:
        S=F[i][:, x0:x1]
        r=cv2.matchTemplate(S,T,cv2.TM_CCOEFF_NORMED)
        x,y,mx=subpix(r)
        res.append((i,x+x0,y,mx))
    return res
if __name__=='__main__':
    v=sys.argv[1]; tf=int(sys.argv[2]); box=list(map(int,sys.argv[3].split(','))); x0,x1=map(int,sys.argv[4].split(','))
    frs=range(int(sys.argv[5]),int(sys.argv[6]))
    R=track(v,tf,box,x0,x1,frs)
    for i,x,y,mx in R: print(i,'%.2f %.2f %.3f'%(x,y,mx))
    t=np.array([r[0] for r in R],float); y=np.array([r[2] for r in R])
    for lo,hi in [(0,len(t)),(2,len(t)),(3,len(t)-1)]:
        p=np.polyfit(t[lo:hi],y[lo:hi],2); res=y[lo:hi]-np.polyval(p,t[lo:hi])
        print('fit frames %d-%d: a=%.4f px/f^2  t0=%.3f  rms=%.3f'%(t[lo],t[hi-1],2*p[0],-p[1]/(2*p[0]),res.std()))
