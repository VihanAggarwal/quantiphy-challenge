import cv2, numpy as np
f=cv2.imread('/home/user/quantiphy-challenge/research/next/labaudit2/0023/frames/captured_0023s_48.png').astype(np.float32)
B,G,R=f[...,0],f[...,1],f[...,2]
# background is blue-ish (B>R); wood is R>B
wood=(R-B>25)
wood[:, :]&=True
m=wood.astype(np.uint8)
n,lab,st,cen=cv2.connectedComponentsWithStats(m)
k=1+np.argmax(st[1:,4]); m=(lab==k)
ys,xs=np.nonzero(m)
print('wood bbox',xs.min(),xs.max(),ys.min(),ys.max())
# left boundary per row, right boundary per row
rows=range(ys.min(),ys.max()+1)
L=[];Rr=[]
for y in rows:
    xx=np.nonzero(m[y])[0]
    if len(xx): L.append((y,xx.min())); Rr.append((y,xx.max()))
for y,x in L[::5]: print('L',y,x, 'R', dict(Rr)[y])
# top boundary per column
T=[]
for x in range(xs.min(),xs.max()+1):
    yy=np.nonzero(m[:,x])[0]
    if len(yy): T.append((x,yy.min(),yy.max()))
for t in T[::20]: print('T',t)
