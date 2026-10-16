import cv2, numpy as np
B='/home/user/quantiphy-challenge/research/next/labaudit/0038'
for tag in ('o','x'):
    fr=np.load(f'{B}/frames/{tag}.npy')
    tiles=[]
    for i in range(27,41):
        t=cv2.resize(fr[i][440:540, 580:840],None,fx=2,fy=2,interpolation=cv2.INTER_NEAREST)
        cv2.putText(t,f'{i}',(5,20),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2)
        tiles.append(t)
    rows=[np.hstack(tiles[k:k+2]) for k in range(0,len(tiles),2)]
    cv2.imwrite(f'{B}/crop_pass_{tag}.png', np.vstack(rows))
