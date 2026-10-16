import cv2,numpy as np,sys
d='/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure/frames'
v=sys.argv[1]
for i in range(int(sys.argv[2]),int(sys.argv[3])):
    f=cv2.imread(f'{d}/{v}_{i:02d}.png')
    if v=='bx':
        m=(f.astype(int).sum(2)>40)
    else:
        b,g,r=[f[:,:,k].astype(int) for k in range(3)]
        m=~((g>200)&(b<60)&(r<60))
    m[690:,1000:]=False
    m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,l,st,c=cv2.connectedComponentsWithStats(m)
    out=[]
    for k in range(1,n):
        if st[k,4]>40:
            ys,xs=np.where(l==k); col=f[ys,xs].mean(0)
            out.append(f'({c[k][0]:.1f},{c[k][1]:.1f}) A{st[k,4]} wh{st[k,2]}x{st[k,3]} bgr{tuple(col.round().astype(int))}')
    print(i,' | '.join(out))
