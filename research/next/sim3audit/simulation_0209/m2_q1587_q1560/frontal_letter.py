import cv2,numpy as np,sys
fn=sys.argv[1]
im=cv2.imread(fn); gr=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(float); gr=cv2.GaussianBlur(gr,(3,3),0.7)
# letter lum ~165, desk ~50 ; T=105
T=float(sys.argv[2]) if len(sys.argv)>2 else 105
def cross(arr,xs):
    for i in range(len(arr)-1):
        if (arr[i]-T)*(arr[i+1]-T)<=0 and arr[i]!=arr[i+1]:
            return xs[i]+(T-arr[i])/(arr[i+1]-arr[i])*(xs[i+1]-xs[i])
    return np.nan
def fit(P):
    P=np.array([p for p in P if np.all(np.isfinite(p))]); A=np.c_[P[:,1],np.ones(len(P))]
    c=np.linalg.lstsq(A,P[:,0],rcond=None)[0]; r=P[:,0]-A@c; return c,np.sqrt(np.mean(r**2)),len(P)
L=[(cross(gr[v,1175:1215],np.arange(1175,1215)),v) for v in range(986,999)]
R=[(cross(gr[v,1400:1360:-1],np.arange(1400,1360,-1)),v) for v in range(986,999)]
cL,rl,nl=fit(L); cR,rr,nr=fit(R)
# front edge: scan up columns
F=[cross(gr[1012:975:-1,x],np.arange(1012,975,-1)) for x in list(range(1205,1240))+list(range(1365,1376))]
B=[cross(gr[970:995,x],np.arange(970,995)) for x in list(range(1200,1215))+list(range(1366,1376))]
F=np.array(F); B=np.array(B)
print('left edge x=',cL.round(3),'rms',round(rl,3),' right edge',cR.round(3),'rms',round(rr,3))
print('front v: median',np.nanmedian(F).round(2),'left part',np.nanmedian(F[:35]).round(2),'right part',np.nanmedian(F[35:]).round(2))
print('back v: median',np.nanmedian(B).round(2),'left',np.nanmedian(B[:15]).round(2),'right',np.nanmedian(B[15:]).round(2))
inl=np.load(fn.replace('.png','_inlay.npy'))
for v in [np.nanmedian(B),(np.nanmedian(B)+np.nanmedian(F))/2,np.nanmedian(F)]:
    w=(cR[0]-cL[0])*v+cR[1]-cL[1]; iw=(inl[2]-inl[0])*v+inl[3]-inl[1]
    print(f'v={v:.2f} letter px={w:.2f} inlay px={iw:.2f} ratio={w/iw:.5f}')
