import cv2, numpy as np, sys
W='/home/user/quantiphy-challenge/research/next/labaudit/0035/remeasure_work/'
def orange_mask(f):
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    return ((hsv[...,0]<22)&(hsv[...,1]>110)&(hsv[...,2]>60)).astype(np.uint8)
def blob(f, near=None, rad=80):
    m=orange_mask(f)
    if near is not None:
        mm=np.zeros_like(m); x,y=near
        mm[max(0,y-rad):y+rad,max(0,x-rad):x+rad]=1; m=m*mm
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    j=1+np.argmax(st[1:,4])
    return (lab==j), cen[j], st[j]
def edge_fit(f, c0, r0, nang=180):
    """radial max-gradient edge points along rays; fit ellipse"""
    g=cv2.GaussianBlur(cv2.cvtColor(f,cv2.COLOR_BGR2HSV)[...,1].astype(np.float32),(3,3),0)  # saturation
    pts=[]
    for a in np.linspace(0,2*np.pi,nang,endpoint=False):
        rs=np.arange(0.4*r0,1.6*r0,0.25)
        xs=c0[0]+rs*np.cos(a); ys=c0[1]+rs*np.sin(a)
        ok=(xs>1)&(xs<f.shape[1]-2)&(ys>1)&(ys<f.shape[0]-2)
        if ok.sum()<10: continue
        v=cv2.remap(g,xs[ok].astype(np.float32).reshape(1,-1),ys[ok].astype(np.float32).reshape(1,-1),cv2.INTER_LINEAR)[0]
        d=-np.gradient(v)
        k=np.argmax(d)
        pts.append((xs[ok][k],ys[ok][k],d[k]))
    return np.array(pts)
def fit_ellipse(P):
    e=cv2.fitEllipse(P[:,:2].astype(np.float32))
    return e
if __name__=='__main__':
    v=sys.argv[1]
    F=np.load(W+v+'.npy')
    near=(830,280)
    for i in range(len(F)):
        try:
            m,c,st=blob(F[i],near)
        except Exception as ex:
            print(i,'none'); continue
        if st[4]<300: print(i,'small',st); continue
        r0=np.sqrt(st[4]/np.pi)
        P=edge_fit(F[i],c,r0)
        # robust: drop points with weak gradient or far from median radius
        rr=np.hypot(P[:,0]-c[0],P[:,1]-c[1])
        keep=(np.abs(rr-np.median(rr))<0.25*np.median(rr))&(P[:,2]>0.3*np.median(P[:,2]))
        e=fit_ellipse(P[keep])
        (ex,ey),(a,b),ang=e
        print(i, 'blobc=(%.1f,%.1f) area=%d eqd=%.1f bbox=%dx%d | ell c=(%.1f,%.1f) axes=%.1f,%.1f ang=%.0f n=%d'%(c[0],c[1],st[4],2*r0,st[2],st[3],ex,ey,min(a,b),max(a,b),ang,keep.sum()))
        near=(int(ex),int(ey))
