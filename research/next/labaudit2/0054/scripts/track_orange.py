from common import *
import sys, json
def seg(im, lo=(3,110,70), hi=(22,255,255)):
    h=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    m=cv2.inRange(h,np.array(lo),np.array(hi))
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    return m
res={}
for v in sys.argv[1:]:
    L=frames(v); out=[]
    for k,im in enumerate(L):
        m=seg(im)
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        if n<2: out.append(None); continue
        i=1+np.argmax(st[1:,4])
        if st[i,4]<150: out.append(None); continue
        ys,xs=np.nonzero(lab==i)
        cnt=np.stack([xs,ys],1).astype(np.float32)
        (cx,cy),r=cv2.minEnclosingCircle(cnt)
        hull=cv2.convexHull(cnt)
        e=cv2.fitEllipse(hull) if len(hull)>=5 else None
        out.append(dict(k=k,mx=float(xs.mean()),my=float(ys.mean()),bx=(xs.min()+xs.max())/2,by=(ys.min()+ys.max())/2,w=int(xs.max()-xs.min()+1),h=int(ys.max()-ys.min()+1),area=int(st[i,4]),ecx=e[0][0],ecy=e[0][1],ea=max(e[1]),eb=min(e[1])))
    res[v]=out
    for o in out:
        if o: print(v,o['k'],cap(o['k']),f"m=({o['mx']:.1f},{o['my']:.1f}) bb=({o['bx']:.1f},{o['by']:.1f}) wh={o['w']}x{o['h']} ell=({o['ecx']:.1f},{o['ecy']:.1f}) {o['ea']:.1f}/{o['eb']:.1f} A={o['area']}")
json.dump(res,open(OUT+'/orange_tracks_'+'_'.join(sys.argv[1:])+'.json','w'))
