import cv2,sys,numpy as np
# usage: strip.py video out.jpg scale x0 y0 x1 y1 f1 f2 ...  -> horizontal montage of crops
v,out=sys.argv[1],sys.argv[2]; sc=float(sys.argv[3]); x0,y0,x1,y1=map(int,sys.argv[4:8]); fs=list(map(int,sys.argv[8:]))
c=cv2.VideoCapture(v); ims=[]
for f in fs:
    c.set(cv2.CAP_PROP_POS_FRAMES,f); ok,im=c.read(); im=im[y0:y1,x0:x1].copy()
    im=cv2.resize(im,None,fx=sc,fy=sc,interpolation=cv2.INTER_AREA if sc<1 else cv2.INTER_NEAREST)
    cv2.putText(im,str(f),(5,25),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2)
    ims.append(im); ims.append(np.full((im.shape[0],4,3),255,np.uint8))
cv2.imwrite(out,np.hstack(ims))
