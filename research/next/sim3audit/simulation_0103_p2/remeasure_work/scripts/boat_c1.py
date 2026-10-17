from vio import *
import cv2
fr=load('0024_segmented')
N=len(fr)
# boat mask: non-white below y=315
res=[]
for k in range(N):
    f=fr[k].astype(int)
    m=(f.min(axis=2)<225); m[:315]=False
    ys,xs=np.nonzero(m)
    # red hull: R>150, G<120
    red=(f[:,:,2]>150)&(f[:,:,1]<130)&(f[:,:,0]<130); red[:315]=False
    ry,rx=np.nonzero(red)
    res.append([k, xs.min(), xs.max(), ys.min(), ys.max(), xs.mean(), ys.mean(), rx.min(), rx.max(), rx.mean(), ry.mean()])
res=np.array(res,float)
np.set_printoptions(suppress=True, precision=1, linewidth=160)
print(res[::6])
# template matching displacement 24->48 using hull+cabin region
def disp(a,b):
    A=fr[a]; B=fr[b]
    ys,xs=np.nonzero((A.min(axis=2)<225)[315:]); 
    x0,x1,y0,y1=xs.min(),xs.max(),ys.min()+315,ys.max()+315
    x0=max(x0,0); 
    T=A[y0:y1, x0:min(x1,955)]
    r=cv2.matchTemplate(B,T,cv2.TM_CCOEFF_NORMED)
    _,mx,_,loc=cv2.minMaxLoc(r)
    # subpixel
    yy,xx=loc[1],loc[0]
    def sp(c,l,rr): 
        d=(l-rr)/(2*(l-2*c+rr)); return d
    dx=sp(r[yy,xx],r[yy,xx-1],r[yy,xx+1]); dy=sp(r[yy,xx],r[yy-1,xx],r[yy+1,xx])
    return xx+dx-x0, yy+dy-y0, mx
for a,b in [(24,48),(12,36),(36,60),(0,24)]:
    print(a,b,disp(a,b))
