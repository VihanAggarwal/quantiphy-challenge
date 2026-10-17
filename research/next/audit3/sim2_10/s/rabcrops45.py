import cv2, numpy as np, sys
c=sys.argv[1]; csvf=sys.argv[2]; cols=[int(v) for v in sys.argv[3].split(',')]  # rx,ry,rw,rh,rcx,rcy col idx
b=np.loadtxt(csvf,delimiter=',')
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{c}.mp4')
tiles=[]
for f in [5,15,25,35,45,55,65]:
    cap.set(cv2.CAP_PROP_POS_FRAMES,f); ok,im=cap.read()
    x,y,w,h=b[f,cols[:4]].astype(int); cx=int(b[f,cols[4]]); cy=int(b[f,cols[5]])
    cr=im[cy-50:cy+50, cx-65:cx+65].copy()
    cv2.rectangle(cr,(x-(cx-65),y-(cy-50)),(x+w-(cx-65),y+h-(cy-50)),(0,0,255),1)
    cr=cv2.resize(cr,None,fx=3,fy=3,interpolation=cv2.INTER_NEAREST)
    cv2.putText(cr,f'f{f} w{w} h{h}',(5,290),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,0,0),2)
    tiles.append(cr)
out=np.vstack([np.hstack(tiles[:4]),np.hstack(tiles[4:]+[np.zeros_like(tiles[0])])])
cv2.imwrite(f'/home/user/quantiphy-challenge/research/next/audit3/sim2_10/png/rab_{c}.png',out)
