from util import *
fr=frames('0167'); st=np.stack([f[450:800].astype(np.int16) for f in fr]); bg=np.median(st,axis=0)
rows=[]
for i in range(0,80):
    d=(np.abs(st[i]-bg).max(axis=2)>40).astype(np.uint8)
    d=cv2.morphologyEx(d,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,stats,cen=cv2.connectedComponentsWithStats(d)
    big=sorted([(s[4],s[0],s[0]+s[2],s[1]+450,s[1]+s[3]+450,c[0],c[1]+450) for s,c in zip(stats[1:],cen[1:]) if s[4]>300],reverse=True)
    rows.append(big)
    if i%4==0: print(i,[(b[0],b[1],b[2],b[3],b[4],round(b[5],1)) for b in big[:3]])
