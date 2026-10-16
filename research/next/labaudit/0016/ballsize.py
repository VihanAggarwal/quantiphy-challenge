import cv2,numpy as np
f=711.0; cx,cy=640,360
def mask_ball(i,rend='x'):
    im=cv2.imread('frames/f%s_%02d.png'%(rend,i)).astype(int)
    b,g,r=im[...,0],im[...,1],im[...,2]
    notgreen=~((g>150)&(g>r+60)&(g>b+60))
    m=notgreen.astype(np.uint8); m[680:,1000:]=0
    n,lab,st,cen=cv2.connectedComponentsWithStats(m,8)
    best=None
    for k in range(1,n):
        a,x,y,w,h=st[k,4],st[k,0],st[k,1],st[k,2],st[k,3]
        if 3000<a<20000 and x>450: best=k
    if best is None: return None
    return lab==best, cen[best]
pos={}
for i in range(32,41):
    r=mask_ball(i)
    if r is None: continue
    pos[i]=r[1]
for i in range(32,41):
    if i not in pos: continue
    m,c=mask_ball(i)
    a=i-1 if i-1 in pos else i; b=i+1 if i+1 in pos else i
    d=pos[b]-pos[a]; d=d/np.linalg.norm(d); p=np.array([-d[1],d[0]])
    ys,xs=np.nonzero(m); P=np.stack([xs,ys],1).astype(float)
    along=P@d; perp=P@p
    # robust extents (1st-99th pct) and full
    ext=lambda v:(v.max()-v.min()+1, np.percentile(v,99.5)-np.percentile(v,0.5))
    # area-equivalent
    print(i, 'cen',np.round(c,1),'dir',np.round(d,2),'along',np.round(ext(along),1),'perp',np.round(ext(perp),1),'area',m.sum(),'eqdiam',round(2*np.sqrt(m.sum()/np.pi),1))
