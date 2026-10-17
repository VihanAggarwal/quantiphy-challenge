from util import *
fr=frames('0166'); st=np.stack([f[500:800].astype(np.int16) for f in fr])
bg=np.median(st,axis=0)
for i in range(0,80,3):
    d=(np.abs(st[i]-bg).max(axis=2)>35).astype(np.uint8)
    n,lab,stats,cen=cv2.connectedComponentsWithStats(d)
    big=[(s[0],s[0]+s[2],s[1]+500,s[1]+s[3]+500,s[4]) for s in stats[1:] if s[4]>400]
    print(i,big)
