from common import *
import numpy as np, cv2, json
fa=frames('a')
M=json.load(open(OUT+'ax_moments.json'))
# background: median of frames far in time (balls elsewhere) -> use frames 0..48 median per pixel in a ROI
stack=np.array([f[200:720,200:700].astype(np.int16) for f in fa])
res=[]
for r in M:
    i=r['i']
    if i<30: continue
    # local background: median over frames i-6..i+6 excluding i-2..i+2
    idx=[k for k in range(max(0,i-8),min(len(fa),i+9)) if abs(k-i)>2]
    bg=np.median(stack[idx],axis=0)
    diff=np.abs(stack[i]-bg).sum(2)
    x,y=int(r['x'])-200,int(r['y'])-200
    h=45
    sub=diff[max(0,y-h):y+h,max(0,x-h):x+h].astype(float)
    # mask out other ball: keep only connected region around the ax centroid
    w=np.clip(sub-40,0,None)
    m=(w>0).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
    cy0,cx0=min(h,y),min(h,x)
    # choose component nearest to center weighted by area
    best=None;bd=1e9
    for k in range(1,n):
        if st[k][4]<30: continue
        d=np.hypot(cen[k][0]-cx0,cen[k][1]-cy0)
        if d<bd: bd=d;best=k
    ww=w*(lab==best)
    yy,xx=np.mgrid[0:sub.shape[0],0:sub.shape[1]]
    S=ww.sum(); ux=(ww*xx).sum()/S+x-cx0+200; uy=(ww*yy).sum()/S+y-cy0+200
    res.append(dict(i=i,obj=r['obj'],ax=(r['x'],r['y']),a=(ux,uy)))
    print(i,r['obj'],'ax=(%.1f,%.1f) a-diff=(%.1f,%.1f) d=(%.1f,%.1f)'%(r['x'],r['y'],ux,uy,ux-r['x'],uy-r['y']))
json.dump(res,open(OUT+'a_centroids.json','w'))
