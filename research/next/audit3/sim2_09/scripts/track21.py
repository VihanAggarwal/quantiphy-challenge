from load import *
S=0.438/120.2
def sub(r,x,y):
    dx=dy=0
    if 0<x<r.shape[1]-1:
        l,c,rr=r[y,x-1],r[y,x],r[y,x+1]; dx=0.5*(l-rr)/(l-2*c+rr)
    if 0<y<r.shape[0]-1:
        l,c,rr=r[y-1,x],r[y,x],r[y+1,x]; dy=0.5*(l-rr)/(l-2*c+rr)
    return x+dx,y+dy
B22=np.load('simulation_0222_B.npy')
out={}
for v in ['simulation_0221','simulation_0222']:
    fr=load(v)
    g=[]
    for f in fr:
        f=cv2.GaussianBlur(f,(3,3),0)
        gx=cv2.Sobel(f,cv2.CV_32F,1,0); gy=cv2.Sobel(f,cv2.CV_32F,0,1)
        g.append(np.sqrt(gx*gx+gy*gy))
    g=np.array(g)
    cy,cx=500,650
    T=g[79][cy-68:cy+68,cx-68:cx+68]
    # mask template to annulus to ignore interior & background
    yy,xx=np.mgrid[-68:68,-68:68]+0.5
    rr=np.sqrt(xx**2+yy**2)
    M=((rr>52)&(rr<66)).astype(np.float32)
    P=[]
    for i in range(len(fr)):
        px,py=B22[i,:2]
        x0=int(px)-68-20; y0=int(py)-68-20
        W=g[i][y0:y0+136+40,x0:x0+136+40]
        r=cv2.matchTemplate(W,T,cv2.TM_CCORR_NORMED,mask=M)
        _,mv,_,ml=cv2.minMaxLoc(r)
        x,y=sub(r,*ml)
        P.append((x0+x+68,y0+y+68,mv))
    P=np.array(P); out[v]=P
    np.save(f'{v}_C.npy',P)
for v,P in out.items():
    sp=np.concatenate([[np.nan],np.linalg.norm(np.diff(P[:,:2],axis=0),axis=1)*24*S])
    print(v,' '.join(f'{i}:{sp[i]:.3f}' for i in range(1,72)))
d=out['simulation_0221'][:,:2]-out['simulation_0222'][:,:2]
print('pos diff 21-22', np.round(d[::6],2).tolist())
