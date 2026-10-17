import numpy as np, cv2
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/'
o=np.load(S+'o.npy').astype(np.float32)
bg=np.median(o,axis=0)   # objects are transient in the fall column
cap=lambda i: i if i<=35 else i+1
for name,(c0,c1) in [('box',(458,512)),('ball',(508,572))]:
    print(name)
    for i in range(31,40):
        d=np.abs(o[i]-bg).max(axis=2)
        m=(d>28).astype(np.uint8)
        roi=np.zeros_like(m); roi[290:625,c0:c1]=1; m=m*roi
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        if n<2: continue
        k=1+np.argmax(st[1:,4]); x0,y0,w,h,a=st[k]
        print('  v%d c%d cx=%.1f cy=%.1f top=%d bot=%d mid=%.1f w=%d a=%d'%(i,cap(i),cen[k][0],cen[k][1],y0,y0+h-1,y0+(h-1)/2,w,a))
