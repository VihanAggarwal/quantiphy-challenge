import cv2,numpy as np,sys
clip=sys.argv[1]; frs=list(map(int,sys.argv[2].split(','))); x0,y0,x1,y1=map(int,sys.argv[3:7]); sc=float(sys.argv[7]); out=sys.argv[8]
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/internet_{clip}.mp4')
ts=[]
for k in frs:
    c.set(cv2.CAP_PROP_POS_FRAMES,k); ok,f=c.read(); t=cv2.resize(f[y0:y1,x0:x1],None,fx=sc,fy=sc,interpolation=cv2.INTER_AREA)
    cv2.putText(t,str(k),(5,20),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2); ts.append(t)
cv2.imwrite(out,np.vstack(ts)); print(np.vstack(ts).shape)
