import cv2, numpy as np, json
from track import cover_mask
from table_track import measure
R1='/home/user/quantiphy-challenge/research/next/labaudit/0023/frames/'
T=json.load(open('cover_track.json'))
tiles=[]
for k in [24,29,30]:
    im=cv2.imread(R1+f'o{k:02d}.png'); m=cover_mask(im)
    cnts,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); cv2.drawContours(im,cnts,-1,(0,0,255),1)
    c=T['o'][k]; cv2.drawMarker(im,(int(round(c['cx'])),int(round(c['cy']))),(255,0,255),cv2.MARKER_CROSS,12,2)
    tiles.append(cv2.resize(im[330:520,460:720],None,fx=2,fy=2,interpolation=cv2.INTER_NEAREST))
for k in [34,35,38]:
    im=cv2.imread(R1+f'o{k:02d}.png'); M=measure('o',k)
    for x,yt,yd,yb,_,_ in M:
        for y,col in [(yt,(0,0,255)),(yd,(255,0,0)),(yb,(0,200,0))]: cv2.circle(im,(int(x),int(round(y))),1,col,-1)
    tiles.append(cv2.resize(im[330:520,460:720],None,fx=2,fy=2,interpolation=cv2.INTER_NEAREST))
for t,k in zip(tiles,[24,29,30,34,35,38]): cv2.putText(t,f'o{k}',(5,25),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2)
cv2.imwrite('overlay.png',np.vstack([np.hstack(tiles[:3]),np.hstack(tiles[3:])]))
