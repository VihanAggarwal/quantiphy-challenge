from util import *
fr=frames('internet_0010_segmented')
P=[]
for i in range(46,86):
    f=fr[i].astype(np.int32)
    m=(f.min(axis=2)<200).astype(np.uint8)
    m[440:,:]=0  # remove person region below 440? ball above
    m[:, :440]=0
    nl,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if nl<2: continue
    k=1+np.argmax(st[1:,4])
    # subpixel: weighted centroid of darkness
    x,y,w,h,a=st[k]
    sub=255-f[y-3:y+h+3,x-3:x+w+3].min(axis=2).astype(float); sub[sub<30]=0
    yy,xx=np.mgrid[y-3:y+h+3,x-3:x+w+3]
    cx=(sub*xx).sum()/sub.sum(); cy=(sub*yy).sum()/sub.sum()
    P.append((i,cx,cy,w,h,a))
P=np.array(P)
for p in P: print(np.round(p,2))
t=P[:,0]
sel=(t>=48)&(t<=83)
cx=np.polyfit(t[sel],P[sel,1],2); cy=np.polyfit(t[sel],P[sel,2],2)
print('x fit',cx,'y fit',cy)
print('resid x',np.std(P[sel,1]-np.polyval(cx,t[sel])),'resid y',np.std(P[sel,2]-np.polyval(cy,t[sel])))
print('median w,h,area',np.median(P[:,3]),np.median(P[:,4]),np.median(P[:,5]), 'eqdiam',2*np.sqrt(np.median(P[:,5])/np.pi))
