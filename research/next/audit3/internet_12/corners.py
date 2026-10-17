import cv2, sys, numpy as np
# corners.py video frame out scale half g x1,y1 x2,y2 ...
p,f,out,scale,half,g=sys.argv[1],int(sys.argv[2]),sys.argv[3],float(sys.argv[4]),int(sys.argv[5]),int(sys.argv[6])
cap=cv2.VideoCapture(p); cap.set(cv2.CAP_PROP_POS_FRAMES,f); ok,im=cap.read()
tiles=[]
for a in sys.argv[7:]:
    cx,cy=map(int,a.split(','))
    x0,y0=cx-half,cy-half; x1,y1=cx+half,cy+half
    c=im[max(y0,0):y1,max(x0,0):x1].copy()
    if c.shape[0]<2*half or c.shape[1]<2*half:
        c=cv2.copyMakeBorder(c,max(0,-y0),2*half-c.shape[0]-max(0,-y0),max(0,-x0),2*half-c.shape[1]-max(0,-x0),cv2.BORDER_CONSTANT)
    c=cv2.resize(c,None,fx=scale,fy=scale,interpolation=cv2.INTER_CUBIC)
    for gx in range((x0//g+1)*g,x1,g):
        X=int((gx-x0)*scale); cv2.line(c,(X,0),(X,c.shape[0]),(0,200,255),1); cv2.putText(c,str(gx),(X+2,12),0,0.35,(0,0,255),1)
    for gy in range((y0//g+1)*g,y1,g):
        Y=int((gy-y0)*scale); cv2.line(c,(0,Y),(c.shape[1],Y),(0,200,255),1); cv2.putText(c,str(gy),(2,Y-2),0,0.35,(0,0,255),1)
    tiles.append(c)
cv2.imwrite(out,np.hstack(tiles))
