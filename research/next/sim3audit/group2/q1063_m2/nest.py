from load import frames; import numpy as np, cv2
F=frames(); 
last=F[59].astype(int); first=F[0].astype(int)
res=[]
for i,f in enumerate(F):
    # region left side
    x0,x1,y0,y1=100,420,1000,1650
    c=f[y0:y1,x0:x1].astype(int)
    d1=np.abs(c-first[y0:y1,x0:x1]).sum(2); d2=np.abs(c-last[y0:y1,x0:x1]).sum(2)
    m=((d1>40)&(d2>40)).astype(np.uint8)   # differs from both start and end -> nest in transit
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: res.append((i,None)); continue
    k=1+np.argmax(st[1:,4])
    if st[k,4]<150: res.append((i,None)); continue
    res.append((i,(cen[k][0]+x0,cen[k][1]+y0,st[k,4],st[k,1]+y0,st[k,1]+st[k,3]+y0)))
for r in res: print(r)
