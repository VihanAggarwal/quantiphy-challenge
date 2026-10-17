from vio import *
import cv2, sys
v=sys.argv[1]; y0=int(sys.argv[2]); y1=int(sys.argv[3]); x0=int(sys.argv[4]) if len(sys.argv)>4 else 0
fr=load(v)
N=len(fr)
def mask(f):
    m=(f.astype(int).min(axis=2)<225); m[:y0]=False; m[y1:]=False; m[:,:x0]=False; return m
res=[]
for k in range(N):
    f=fr[k].astype(int); m=mask(fr[k])
    ys,xs=np.nonzero(m)
    red=(f[:,:,2]>140)&(f[:,:,1]<110)&(f[:,:,0]<110); red&=m
    ry,rx=np.nonzero(red)
    res.append([k, xs.min(), xs.max(), ys.min(), ys.max(), xs.mean(), ys.mean(), rx.mean(), ry.mean(), red.sum()])
res=np.array(res,float)
np.set_printoptions(suppress=True, precision=1, linewidth=160)
print(res[::6])
np.savetxt(W+'boat_%s.txt'%v,res,fmt='%.2f')
def disp(a,b,pad=3):
    A=fr[a]; B=fr[b]; m=mask(A)
    ys,xs=np.nonzero(m)
    xa,xb,ya,yb=xs.min(),xs.max(),ys.min(),ys.max()
    T=A[ya:yb+1, xa:xb+1]
    r=cv2.matchTemplate(B,T,cv2.TM_CCOEFF_NORMED)
    _,mx,_,loc=cv2.minMaxLoc(r)
    yy,xx=loc[1],loc[0]
    sp=lambda c,l,rr:(l-rr)/(2*(l-2*c+rr))
    dx=sp(r[yy,xx],r[yy,xx-1],r[yy,xx+1]); dy=sp(r[yy,xx],r[yy-1,xx],r[yy+1,xx])
    return round(xx+dx-xa,2), round(yy+dy-ya,2), round(mx,3), (xa,xb,ya,yb)
for a,b in [(23,24),(24,48),(12,36),(36,60),(0,24),(47,48)]:
    if b<N: print(a,b,disp(a,b))
