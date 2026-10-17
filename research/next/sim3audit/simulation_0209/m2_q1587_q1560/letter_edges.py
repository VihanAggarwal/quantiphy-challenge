import cv2,numpy as np,sys
fn=sys.argv[1] if len(sys.argv)>1 else 'frames/simulation_0209_f000.png'
gr=cv2.cvtColor(cv2.imread(fn),cv2.COLOR_BGR2GRAY).astype(float)
gr=cv2.GaussianBlur(gr,(3,3),0.7)
T=105
def cross_v(x,ya,yb):  # scan along column x from ya to yb, return subpixel crossing of T
    col=gr[ya:yb+1,x] if ya<yb else gr[yb:ya+1,x][::-1]
    ys=np.arange(ya,yb+1) if ya<yb else np.arange(ya,yb-1,-1)
    for i in range(len(col)-1):
        if (col[i]-T)*(col[i+1]-T)<=0 and col[i]!=col[i+1]:
            return ys[i]+(T-col[i])/(col[i+1]-col[i])*(ys[i+1]-ys[i])
    return np.nan
def cross_h(y,xa,xb):
    row=gr[y,xa:xb+1] if xa<xb else gr[y,xb:xa+1][::-1]
    xs=np.arange(xa,xb+1) if xa<xb else np.arange(xa,xb-1,-1)
    for i in range(len(row)-1):
        if (row[i]-T)*(row[i+1]-T)<=0 and row[i]!=row[i+1]:
            return xs[i]+(T-row[i])/(row[i+1]-row[i])*(xs[i+1]-xs[i])
    return np.nan
def fitline(P):
    P=np.array([p for p in P if np.all(np.isfinite(p))]); m=P.mean(0)
    _,_,Vt=np.linalg.svd(P-m); d=Vt[0]; n=np.array([-d[1],d[0]])
    res=(P-m)@n
    return m,d,np.sqrt(np.mean(res**2)),len(P)
# front edge: scan up from below for cols 1366..1404
front=[(x,cross_v(x,652,630)) for x in range(1366,1405)]
# back edge: scan down from above for cols 1324..1352
back=[(x,cross_v(x,612,628)) for x in range(1325,1352)]
# left edge: scan rightwards from left for rows 627..641
left=[(cross_h(y,1310,1380),y) for y in range(627,641)]
L={}
for name,P in [('front',front),('back',back),('left',left)]:
    m,d,r,n=fitline(P); L[name]=(m,d); print(name,'pt',m.round(2),'dir',d.round(4),'slope',round(d[1]/d[0],4),'rms',round(r,3),n)
def inter(a,b):
    (m1,d1),(m2,d2)=a,b
    A=np.array([d1,-d2]).T; t=np.linalg.solve(A,m2-m1); return m1+t[0]*d1
BL=inter(L['back'],L['left']); FL=inter(L['front'],L['left'])
print('BL',BL.round(2),'FL',FL.round(2))
np.save('letter_lines.npy',np.array([np.r_[L[k][0],L[k][1]] for k in ['front','back','left']]))
