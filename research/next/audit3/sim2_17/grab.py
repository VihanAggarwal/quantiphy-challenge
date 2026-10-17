import cv2,sys
v=sys.argv[1]; out=sys.argv[2]; frames=[int(x) for x in sys.argv[3].split(',')]
scale=float(sys.argv[4]) if len(sys.argv)>4 else 0.5
crop=None
if len(sys.argv)>5:
    crop=[int(x) for x in sys.argv[5].split(',')]  # x0,y0,x1,y1
c=cv2.VideoCapture(f'data/QuantiPhy/{v}.mp4')
imgs=[]
for f in frames:
    c.set(cv2.CAP_PROP_POS_FRAMES,f); ok,im=c.read()
    if crop: im=im[crop[1]:crop[3],crop[0]:crop[2]]
    im=cv2.resize(im,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA if scale<1 else cv2.INTER_NEAREST)
    cv2.putText(im,str(f),(10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
    imgs.append(im)
import numpy as np
cv2.imwrite(out,np.vstack(imgs))
