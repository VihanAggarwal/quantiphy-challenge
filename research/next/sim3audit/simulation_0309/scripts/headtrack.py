# Track the grey head patch over all frames of 0302; test constant-velocity projective model
import cv2, numpy as np
bg=np.load('bg0302.npy').astype(np.float32)
d=np.load('joint0302.npz'); vp=d['vp']
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0302.mp4')
pts=[];i=0
while True:
    ok,f=cap.read()
    if not ok: break
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    dd=np.abs(f.astype(np.float32)-bg).sum(2)
    m=((hsv[:,:,2]>115)&(dd>90)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n>1:
        k=1+np.argmax(st[1:,4]); pts.append((i,cen[k][0],cen[k][1],st[k][4]))
    i+=1
P=np.array(pts)
for row in P[::4]: print('%d %.1f %.1f %d'%tuple(row))
np.save('head0302.npy',P)
