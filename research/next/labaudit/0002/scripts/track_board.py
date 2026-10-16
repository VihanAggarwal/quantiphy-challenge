import cv2, numpy as np
# yellowness of the faint (composited) ball on the white board: (R+G)/2 - B, board white ~0
B=cv2.imread('frames/f00.png')
mask=cv2.imread('boardmask.png',0)>0
mask=cv2.erode(mask.astype(np.uint8),np.ones((5,5),np.uint8)).astype(bool)
out=[]
for i in range(24,37):
    f=cv2.imread(f'frames/f{i:02d}.png').astype(float)
    y=(f[...,2]+f[...,1])/2-f[...,0]
    y=cv2.GaussianBlur(y,(7,7),0)
    if i<=29:
        reg=np.zeros_like(mask); reg[255:300,595:640]=True
    else:
        reg=mask
    yy=np.where(reg,y,-1e9)
    py,px=np.unravel_index(np.argmax(yy),yy.shape)
    pk=y[py,px]
    m=(yy>0.5*pk)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m.astype(np.uint8))
    k=lab[py,px]; ys,xs=np.nonzero(lab==k); w=y[ys,xs]
    cx=(w*xs).sum()/w.sum(); cy=(w*ys).sum()/w.sum()
    out.append((i,cx,cy)); print(i,'(%.1f,%.1f) peak %.0f size %dx%d'%(cx,cy,pk,st[k][2],st[k][3]))
np.save('scripts/track_board.npy',np.array(out))
