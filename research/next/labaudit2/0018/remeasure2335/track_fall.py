import numpy as np, cv2
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/'
x=np.load(S+'x.npy')
for i in range(26,49):
    f=x[i]
    m=(f.min(axis=2)<235).astype(np.uint8)
    # restrict to region right of left person body and below arms
    roi=np.zeros_like(m); roi[180:650,440:640]=1
    m=m*roi
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    comps=[(st[k,4],cen[k],st[k,:4]) for k in range(1,n) if st[k,4]>80]
    print(i,[(a,tuple(np.round(c,1)),tuple(b)) for a,c,b in sorted(comps,key=lambda t:-t[0])[:4]])
