import cv2, numpy as np
out='/home/user/quantiphy-challenge/research/next/sim3audit/simulation_0103_p1/frames'
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0027.mp4')
fr=[]
while True:
    ok,img=cap.read()
    if not ok: break
    fr.append(img)
print(len(fr))
# crop around person
tiles=[]
for f in [0,12,24,36,48,60,72]:
    c=fr[f][320:460,360:520]
    c=cv2.resize(c,None,fx=4,fy=4,interpolation=cv2.INTER_NEAREST)
    cv2.putText(c,str(f),(5,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
    tiles.append(c)
cv2.imwrite(f'{out}/s27_person_strip.png',np.hstack(tiles[:4]))
cv2.imwrite(f'{out}/s27_person_strip2.png',np.hstack(tiles[4:]))
