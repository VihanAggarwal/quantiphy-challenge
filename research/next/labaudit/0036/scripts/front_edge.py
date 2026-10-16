import cv2, numpy as np
im=cv2.imread('frames/captured_0036x/f45.png').astype(np.float32)
g=im.mean(axis=2)
for x in [250,350,450,550,650,750,850,950]:
    col=g[560:640,x]
    d=np.diff(col)
    print(x,' '.join('%d:%d'%(560+i,v) for i,v in enumerate(col) if i%2==0))
