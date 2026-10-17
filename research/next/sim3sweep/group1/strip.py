import cv2, sys, numpy as np
# usage: strip.py clip x0 y0 x1 y1 scale frames(comma) out
clip=sys.argv[1]; x0,y0,x1,y1=map(int,sys.argv[2:6]); s=float(sys.argv[6]); fr=[int(a) for a in sys.argv[7].split(',')]; out=sys.argv[8]
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/%s.mp4'%clip)
ims=[]
for f in fr:
    cap.set(cv2.CAP_PROP_POS_FRAMES,f); ok,im=cap.read(); c=im[y0:y1,x0:x1].copy()
    c=cv2.resize(c,None,fx=s,fy=s,interpolation=cv2.INTER_CUBIC if s>1 else cv2.INTER_AREA)
    cv2.putText(c,str(f),(5,25),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2); ims.append(c)
n=len(ims); cols=int(sys.argv[9]) if len(sys.argv)>9 else n
rows=[]
for i in range(0,n,cols):
    r=ims[i:i+cols]
    while len(r)<cols: r.append(np.zeros_like(ims[0]))
    rows.append(np.hstack(r))
cv2.imwrite(out,np.vstack(rows)); print(out)
