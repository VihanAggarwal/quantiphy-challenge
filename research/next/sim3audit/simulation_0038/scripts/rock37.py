import cv2, numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0037_segmented.mp4')
cap.set(cv2.CAP_PROP_POS_FRAMES,24); ok,f=cap.read()
g=f.astype(np.int16); m=((255-g.min(axis=2))>25).astype(np.uint8)
m[:, 760:]=0
n,lab,st,cen=cv2.connectedComponentsWithStats(m)
k=1+np.argmax(st[1:,4]); r=(lab==k)
ys,xs=np.nonzero(r)
print('bbox', xs.min(), xs.max(), ys.min(), ys.max())
for x in list(range(xs.min(),xs.max(),40))+[xs.max()]:
    col=np.nonzero(r[:,x])[0]
    print(x, col.min(), col.max(), col.max()-col.min())
