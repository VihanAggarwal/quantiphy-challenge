from util import *
fr=frames('simulation_0078')
n=len(fr)
bg=np.median(np.stack([fr[i] for i in range(0,n,3)]),axis=0).astype(np.float32)
for i in range(0,n,4):
    d=np.abs(fr[i].astype(np.float32)-bg).max(axis=2)
    m=(d>40).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    nl,lab,st,cen=cv2.connectedComponentsWithStats(m)
    bl=[(st[k,4],cen[k][0],cen[k][1],st[k,0],st[k,0]+st[k,2]) for k in range(1,nl) if st[k,4]>300]
    bl.sort(key=lambda b:b[1])
    print(i, ' | '.join('A%d c%.1f,%.1f x%d-%d'%b for b in bl))
