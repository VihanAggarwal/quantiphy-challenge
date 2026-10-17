import cv2, numpy as np
b=np.loadtxt('/home/user/quantiphy-challenge/research/next/audit3/sim2_10/top46.csv',delimiter=',')
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0246.mp4')
tiles=[]
for f in [5,15,25,35,45,55,65]:
    cap.set(cv2.CAP_PROP_POS_FRAMES,f); ok,im=cap.read()
    x,y,w,h=b[f,7:11].astype(int)
    cx=int(b[f,11]); cy=int(b[f,12])
    cr=im[cy-60:cy+60, cx-80:cx+80].copy()
    # mark mask bbox in red
    cv2.rectangle(cr,(x-(cx-80),y-(cy-60)),(x+w-(cx-80),y+h-(cy-60)),(0,0,255),1)
    # ticks every 10 px along top
    for k in range(0,160,10): cr[0:4 if k%50 else 8,k]=(0,255,255)
    cr=cv2.resize(cr,None,fx=3,fy=3,interpolation=cv2.INTER_NEAREST)
    cv2.putText(cr,f'f{f} w{w}',(5,350),cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,0,0),2)
    tiles.append(cr)
out=np.vstack([np.hstack(tiles[:4]),np.hstack(tiles[4:]+[np.zeros_like(tiles[0])])])
cv2.imwrite('/home/user/quantiphy-challenge/research/next/audit3/sim2_10/png/rab46.png',out)
