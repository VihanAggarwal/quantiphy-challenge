import cv2,numpy as np,sys
fn=sys.argv[1] if len(sys.argv)>1 else 'frames/simulation_0204_f000.png'
im=cv2.imread(fn).astype(float); im=cv2.GaussianBlur(im,(3,3),0.7)
G=im[...,1]; gr=cv2.cvtColor(im.astype(np.uint8),cv2.COLOR_BGR2GRAY).astype(float)
def cross(arr,xs,T):
    for i in range(len(arr)-1):
        if (arr[i]-T)*(arr[i+1]-T)<=0 and arr[i]!=arr[i+1]:
            return xs[i]+(T-arr[i])/(arr[i+1]-arr[i])*(xs[i+1]-xs[i])
    return np.nan
def fit(P):
    P=np.array([p for p in P if np.all(np.isfinite(p))]); 
    A=np.c_[P[:,1],np.ones(len(P))]; c,res,_,_=np.linalg.lstsq(A,P[:,0],rcond=None)  # x = a*v + b
    r=P[:,0]-A@c; return c, np.sqrt(np.mean(r**2)), len(P)
# inlay left boundary: scan right from wood into leather. threshold on G between wood(~47) and leather(~100) -> 72
left=[]
for v in range(962,1050,2):
    xs=np.arange(150,420); x=cross(G[v,150:420][::1],xs,72)
    # first crossing after wood: need to skip background->wood; background G=78 > 72 ... handle: start after silhouette
    row=G[v,150:420]; # find first index where G<60 (wood), then find crossing above 72
    i0=np.argmax(row<60); x=cross(row[i0:],xs[i0:],72); left.append((x,v))
cl,rl,nl=fit(left); print('inlay left x=a v+b',cl.round(4),'rms',round(rl,3),nl)
right=[]
for v in range(962,1050,2):
    xs=np.arange(1700,1960); row=G[v,1700:1960]
    # scan from right(background ~91) leftward: background->wood(<40)->band(>55)
    rr=row[::-1]; xr=xs[::-1]; i0=np.argmax(rr<42); x=cross(rr[i0:],xr[i0:],55); right.append((x,v))
cr,rr_,nr=fit(right); print('inlay right',cr.round(4),'rms',round(rr_,3),nr)
for v in [962,1000,1050]: print(v,'xl',round(cl[0]*v+cl[1],1),'xr',round(cr[0]*v+cr[1],1))
np.save('frontal_inlay.npy',np.r_[cl,cr])
