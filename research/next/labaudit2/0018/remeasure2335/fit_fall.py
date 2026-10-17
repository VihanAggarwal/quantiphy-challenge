import numpy as np, cv2
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/'
x=np.load(S+'x.npy'); s=np.load(S+'s.npy'); o=np.load(S+'o.npy')
def cap(i):  # video frame -> capture frame index (drop between video 35 and 36)
    return i if i<=35 else i+1
def blobs(f, thr, render):
    if render=='x':
        m=(f.min(axis=2)<thr).astype(np.uint8)
    else:  # s render: background bluish gradient; object pixels differ from bg; use x mask style on s? use saturation/colour distance to median bg
        raise
    return m
res={}
for name,cx0,cx1 in [('box',455,512),('ball',505,575)]:
    rows=[]
    for i in range(30,40):
        f=x[i]
        m=(f.min(axis=2)<240).astype(np.uint8)
        roi=np.zeros_like(m); roi[285:620,cx0:cx1]=1   # below the arms
        m=m*roi
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        if n<2: continue
        k=1+np.argmax(st[1:,4])
        x0,y0,w,h,a=st[k]
        rows.append((i,cap(i),cen[k][0],cen[k][1],y0,y0+h,a,w,h))
    res[name]=rows
    print(name)
    for r in rows: print('  v%d c%d cx=%.1f cy=%.1f top=%d bot=%d area=%d w=%d h=%d'%r)
import numpy.polynomial.polynomial as P
def fit(rows,col,sel):
    t=np.array([r[1] for r in rows if sel(r)],float); y=np.array([r[col] for r in rows if sel(r)],float)
    c=np.polyfit(t,y,2); resid=y-np.polyval(c,t)
    return 2*c[0], np.abs(resid).max(), len(t)
for name,rng in [('box',(33,38)),('ball',(33,38))]:
    for col,lab in [(3,'cy'),(4,'top'),(5,'bot')]:
        for lo in [32,33,34]:
            a,r,n=fit(res[name],col,lambda R: lo<=R[0]<=rng[1])
            Z=711*9.8/(a*625)
            print(name,lab,'from v%d'%lo,'a=%.3f px/fr^2  maxres=%.1f n=%d  Z=%.3f m'%(a,r,n,Z))
