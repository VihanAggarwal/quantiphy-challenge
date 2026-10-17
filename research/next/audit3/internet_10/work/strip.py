import cv2,numpy as np,sys
# strip.py clip f0 f1 x0 y0 x1 y1 scale out
clip=sys.argv[1]; f0,f1=int(sys.argv[2]),int(sys.argv[3]); x0,y0,x1,y1=map(int,sys.argv[4:8]); sc=float(sys.argv[8]); out=sys.argv[9]
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/internet_{clip}.mp4'); c.set(cv2.CAP_PROP_POS_FRAMES,f0)
tiles=[]
for k in range(f0,f1+1):
    ok,f=c.read(); t=cv2.resize(f[y0:y1,x0:x1],None,fx=sc,fy=sc,interpolation=cv2.INTER_AREA)
    cv2.putText(t,str(k),(5,20),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2)
    # tick marks every 100px of original x
    for xx in range((x0//100+1)*100,x1,100):
        X=int((xx-x0)*sc); cv2.line(t,(X,0),(X,8),(255,0,0),1)
    tiles.append(t)
cv2.imwrite(out,np.vstack(tiles)); print(np.vstack(tiles).shape)
