import cv2, numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0038_segmented.mp4')
fr=[]
while True:
    ok,f=cap.read()
    if not ok: break
    fr.append(f)
tiles=[]
for i in [2,26,50,74]:
    # find person via non-white comp near expected
    g=fr[i].astype(np.int16); m=((255-g.min(axis=2))>30).astype(np.uint8)
    m[:700]=0
    ys,xs=np.nonzero(m)
    x0=xs.min(); y0=ys.min()
    print(i, x0, y0, xs.max(), ys.max())
    c=fr[i][y0-5:y0+60, x0-5:x0+45]
    s=8
    c=cv2.resize(c,None,fx=s,fy=s,interpolation=cv2.INTER_NEAREST)
    for y in range(0,c.shape[0],s): c[y,:]=(0,0,255) if ((y//s)%10==0) else (220,220,255)
    for x in range(0,c.shape[1],s): c[:,x]=(0,0,255) if ((x//s)%10==0) else (220,220,255)
    cv2.putText(c,f'{i} x0={x0-5} y0={y0-5}',(5,20),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,0,0),2)
    tiles.append(c)
cv2.imwrite('frames/person38_zoom.png',np.hstack(tiles))
