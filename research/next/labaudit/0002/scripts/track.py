import cv2, numpy as np
bgs=np.median(np.stack([cv2.imread(f'frames/f{i:02d}.png').astype(float) for i in [45,46,47,48]]),0)
rows=[]
for i in range(0,45):
    f=cv2.imread(f'frames/f{i:02d}.png').astype(float)
    d=np.linalg.norm(f-bgs,axis=2)
    d[:,:540]=0; d[:,700:]=0; d[:250]=0
    d=cv2.GaussianBlur(d,(5,5),0)
    y,x=np.unravel_index(np.argmax(d),d.shape)
    m=d>0.5*d[y,x]
    n,lab,st,cen=cv2.connectedComponentsWithStats(m.astype(np.uint8))
    k=lab[y,x]
    w=d*(lab==k)
    ys,xs=np.nonzero(lab==k)
    cxw=(w[ys,xs]*xs).sum()/w[ys,xs].sum(); cyw=(w[ys,xs]*ys).sum()/w[ys,xs].sum()
    rows.append((i,cxw,cyw,d[y,x],st[k][2],st[k][3]))
    print(i,'centroid (%.1f,%.1f) peak %.0f bbox w %d h %d'%(cxw,cyw,d[y,x],st[k][2],st[k][3]))
np.save('scripts/track2d.npy',np.array(rows))
