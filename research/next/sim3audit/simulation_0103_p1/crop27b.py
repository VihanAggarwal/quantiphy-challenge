import cv2, numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0027.mp4')
fr=[]
while True:
    ok,img=cap.read()
    if not ok: break
    fr.append(img)
fr=np.array(fr).astype(np.float32)
bg=np.median(fr[:,300:480,350:560],axis=0)
tiles=[]
for f in [24,48]:
    c=fr[f,300:480,350:560]
    d=np.clip((c-bg)*3+128,0,255).astype(np.uint8)
    big=cv2.resize(d,None,fx=5,fy=5,interpolation=cv2.INTER_NEAREST)
    for yy in range(0,180,10):
        cv2.line(big,(0,yy*5),(8,yy*5),(0,0,255),1); cv2.putText(big,str(300+yy),(10,yy*5+4),cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,0,255),1)
    for xx in range(0,210,10):
        cv2.line(big,(xx*5,0),(xx*5,8),(255,0,0),1); cv2.putText(big,str(350+xx),(xx*5-8,20),cv2.FONT_HERSHEY_SIMPLEX,0.3,(255,0,0),1)
    tiles.append(big)
cv2.imwrite('/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p1/frames/s27_diff_24_48.png',np.hstack(tiles))
