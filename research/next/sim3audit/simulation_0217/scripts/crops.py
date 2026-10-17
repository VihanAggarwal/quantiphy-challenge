import cv2, numpy as np, sys
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0212.mp4')
F=[]
while True:
    ok,f=cap.read()
    if not ok: break
    F.append(f)
idx=[0,6,12,18,24,30,36,42,48]
tiles=[]
for i in idx:
    c=F[i][560:1000, 900:1740].copy()
    cv2.putText(c,str(i),(10,40),cv2.FONT_HERSHEY_SIMPLEX,1.2,(0,0,255),3)
    tiles.append(c)
rows=[np.hstack(tiles[k:k+3]) for k in range(0,9,3)]
im=np.vstack(rows)
im=cv2.resize(im,None,fx=0.75,fy=0.75)
cv2.imwrite('frames/dog_tiles.png',im)
