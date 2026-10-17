from util import *
fr=frames('simulation_0020')
n=len(fr)
bg=np.median(np.stack([fr[i] for i in range(60,131,7)]),axis=0).astype(np.float32)
# ball: orange; use HSV
res=[]
for i in range(n):
    f=fr[i]; hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    m=((hsv[...,0]<20)|(hsv[...,0]>170))&(hsv[...,1]>120)&(hsv[...,2]>60)
    m=m.astype(np.uint8)
    nl,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if nl>1:
        k=1+np.argmax(st[1:,4])
        res.append((i,cen[k][0],cen[k][1],st[k,2],st[k,3],st[k,4]))
    else: res.append((i,np.nan,np.nan,0,0,0))
for r in res: print('%d %.1f %.1f %d %d %d'%r)
