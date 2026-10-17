import cv2, numpy as np
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/f36/'
v='captured_0036'
ks=[0,12,14,18,21,22,26,30,33,34,35,36,37,38,40,44]
tiles=[]
for k in ks:
    im=cv2.imread(S+f'{v}/f{k:02d}.png')[330:650,150:1100]
    im=cv2.resize(im,None,fx=0.5,fy=0.5)
    cv2.putText(im,str(k),(10,30),0,1,(0,0,255),2)
    tiles.append(im)
rows=[np.hstack(tiles[i:i+4]) for i in range(0,16,4)]
cv2.imwrite('img/mont.png',np.vstack(rows))
