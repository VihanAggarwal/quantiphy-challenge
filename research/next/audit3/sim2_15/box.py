from util import *
import sys
v=sys.argv[1]
fr=frames(v); n=len(fr)
st=np.stack([f.astype(np.int16) for f in fr])
bg=np.median(st,axis=0)
res=[]
for i in range(n):
    d=(np.abs(st[i]-bg).max(axis=2)>30).astype(np.uint8)
    d=cv2.morphologyEx(d,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    nn,lab,stats,cen=cv2.connectedComponentsWithStats(d)
    if nn<2: res.append(None); continue
    k=1+np.argmax(stats[1:,4]); s=stats[k]
    ys,xs=np.nonzero(lab==k)
    res.append((i,xs.mean(),ys.mean(),s[0],s[0]+s[2],s[1],s[1]+s[3],s[4]))
    print(i,'cen %.1f %.1f'%(xs.mean(),ys.mean()),'bbox x %d-%d y %d-%d'%(s[0],s[0]+s[2],s[1],s[1]+s[3]),'area',s[4])
