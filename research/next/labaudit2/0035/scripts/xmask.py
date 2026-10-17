# soccer/bb size from the x render alone (green bg in ax), compared with the 3-way mask
import sys
from geom import *
take=sys.argv[1]; key=sys.argv[2]
X=frames(take+'x'); tr=load_tr(take)
def xfg(f):
    b,g,r=[f[...,i].astype(int) for i in range(3)]
    if take=='a': bg=(g>200)&(r<80)&(b<80)
    else: bg=(b>245)&(g>245)&(r>245)
    return (~bg).astype(np.uint8)
res={}
for k in sorted(tr[key]):
    d=tr[key][k]; cx,cy=int(d['cx']),int(d['cy']); R=int(d['major']*0.9)+6
    m=xfg(X[k]); sub=np.zeros_like(m); y0,x0=max(cy-R,0),max(cx-R,0); sub[y0:cy+R,x0:cx+R]=m[y0:cy+R,x0:cx+R]
    n,lab,st,cen=cv2.connectedComponentsWithStats(sub,8)
    if n<2: continue
    j=1+np.argmin([np.hypot(cen[i][0]-d['cx'],cen[i][1]-d['cy']) if st[i][4]>200 else 1e9 for i in range(1,n)])
    comp=(lab==j).astype(np.uint8)
    cs,_=cv2.findContours(comp,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); c=max(cs,key=cv2.contourArea)
    A=cv2.contourArea(c); (ex,ey),(a1,a2),ang=cv2.fitEllipse(c)
    res[k]=dict(deq=np.sqrt(4*A/np.pi),minor=min(a1,a2),major=max(a1,a2),cx=ex,cy=ey)
print('frame  3way_deq xonly_deq  3way_min xonly_min  xonly_maj  dcx dcy')
for k in sorted(res):
    d=tr[key][k]; e=res[k]
    print(f"{k:3d} {d['deq']:7.1f} {e['deq']:7.1f} {d['minor']:7.1f} {e['minor']:7.1f} {e['major']:7.1f} {e['cx']-d['cx']:5.1f} {e['cy']-d['cy']:5.1f}")
json.dump({str(k):v for k,v in res.items()},open(f'{OUT}/xmask_{take}_{key}.json','w'))
