import cv2, numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0037_segmented.mp4')
cap2=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0037.mp4')
fr=[];fr2=[]
while True:
    ok,f=cap.read(); ok2,f2=cap2.read()
    if not ok: break
    fr.append(f); fr2.append(f2)
tiles=[]
for i in [2,26,50,66]:
    cx=int(798+41.37*i/24)
    for F in (fr,fr2):
        c=F[i][670:770, cx-30:cx+30]
        c=cv2.resize(c,None,fx=6,fy=6,interpolation=cv2.INTER_NEAREST)
        for y in range(0,c.shape[0],60): c[y,:]=(0,0,255) if (y//60)%5==0 else (200,200,255)
        tiles.append(c)
out=np.hstack(tiles)
cv2.imwrite('frames/person37_crops.png',out)
print(out.shape)
