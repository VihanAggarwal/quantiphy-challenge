import cv2, numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0253.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
bg=fr[0].astype(np.float32)
tiles=[]
for i in (20,30,38):
    d=np.abs(fr[i].astype(np.float32)-bg).sum(2)
    m=(d>40).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
    cx,cy=x+w//2,y+h//2; H=80
    crop=fr[i][cy-H:cy+H,cx-H:cx+H]
    z=cv2.resize(crop,(640,640),interpolation=cv2.INTER_NEAREST)
    for kk in range(0,640,20): cv2.line(z,(kk,0),(kk,639),(0,0,255) if (kk//20)%2==0 else (255,0,0),1); cv2.line(z,(0,kk),(639,kk),(0,0,255) if (kk//20)%2==0 else (255,0,0),1)
    cv2.putText(z,f'{i} ({cx-H},{cy-H})',(5,25),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,255,255),2)
    tiles.append(z); print(i,x,y,w,h,a)
cv2.imwrite('box_crops.png',np.hstack(tiles))
