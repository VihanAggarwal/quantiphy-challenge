import cv2, numpy as np
B='/home/user/quantiphy-challenge/research/next/labaudit/0038'
for tag in ('o','x'):
    fr=np.load(f'{B}/frames/{tag}.npy')
    tiles=[]
    for i in range(0,49,2):
        t=cv2.resize(fr[i][150:650, 100:1200],(440,200))
        cv2.putText(t,f'{i} t={i/24:.2f}',(5,20),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2)
        tiles.append(t)
    while len(tiles)%5: tiles.append(np.zeros_like(tiles[0]))
    rows=[np.hstack(tiles[k:k+5]) for k in range(0,len(tiles),5)]
    cv2.imwrite(f'{B}/sheet_{tag}.png', np.vstack(rows))
