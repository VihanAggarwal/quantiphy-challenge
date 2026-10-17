import cv2, numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0239_segmented.mp4'); c.set(1,0); im=c.read()[1]
m=(im.astype(int).min(2)<240).astype(np.uint8)
n,lab,st,cen=cv2.connectedComponentsWithStats(m)
k=1+np.argmax(st[1:,4]); H=(lab==k)
print('house bbox x',st[k,0],st[k,0]+st[k,2]-1,'y',st[k,1],st[k,1]+st[k,3]-1)
ys,xs=np.nonzero(H)
# bottom boundary per column
print('bottom edge (x: max y):')
for x in range(640,1400,40):
    col=np.nonzero(H[:,x])[0]
    print(x, col.max() if len(col) else None, col.min() if len(col) else None)
print('left/right edge per row (y: minx maxx):')
for y in range(10,760,30):
    row=np.nonzero(H[y])[0]
    print(y, row.min() if len(row) else None, row.max() if len(row) else None)
cv2.imwrite('house_top_mask.png', cv2.resize((H*255).astype(np.uint8),None,fx=0.4,fy=0.4))
