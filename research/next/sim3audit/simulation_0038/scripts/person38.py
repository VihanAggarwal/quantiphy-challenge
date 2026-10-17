import cv2, numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0038_segmented.mp4')
fr=[]
while True:
    ok,f=cap.read()
    if not ok: break
    fr.append(f[760:900,440:620].copy())
fr=np.array(fr).astype(np.int16)
d=[np.abs(fr[i]-fr[i-1]).mean() for i in range(1,len(fr))]
print('person-roi diffs', [ (i+1,round(x,3)) for i,x in enumerate(d)])
# crops
tiles=[]
for i in [0,25,50,74]:
    c=cv2.resize(fr[i].astype(np.uint8),None,fx=5,fy=5,interpolation=cv2.INTER_NEAREST)
    tiles.append(c)
cv2.imwrite('frames/person38_crops.png',np.hstack(tiles))
