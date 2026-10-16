import cv2, numpy as np
R='rs'
bg=np.median(np.stack([cv2.imread(f'frames/{R}_{i:02d}.png').astype(np.float32) for i in range(36,49)]),0)
for i in range(0,26):
    im=cv2.imread(f'frames/{R}_{i:02d}.png').astype(np.float32)
    d=np.abs(im-bg).sum(2)
    d[:, :470]=0; d[:, 680:]=0; d[:250]=0; d[560:]=0
    m=(d>45).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<=1: print(i,'none'); continue
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    print(i, f't={i/24:.3f}', 'bbox',x,y,w,h,'area',a,'cen',np.round(cen[k],1))
