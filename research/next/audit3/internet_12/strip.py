import cv2, sys, numpy as np
# usage: strip.py video out scale x0,y0,x1,y1 f1 f2 ... ; draws grid every 'g' px (full-res coords)
p,out,scale,crop=sys.argv[1],sys.argv[2],float(sys.argv[3]),sys.argv[4]
frames=[int(a) for a in sys.argv[5:]]
x0,y0,x1,y1=map(int,crop.split(','))
g=int(__import__('os').environ.get('GRID','50'))
cap=cv2.VideoCapture(p); tiles=[]
for f in frames:
    cap.set(cv2.CAP_PROP_POS_FRAMES,f); ok,im=cap.read()
    c=im[y0:y1,x0:x1].copy()
    c=cv2.resize(c,None,fx=scale,fy=scale,interpolation=cv2.INTER_CUBIC if scale>1 else cv2.INTER_AREA)
    for gx in range((x0//g+1)*g, x1, g):
        X=int((gx-x0)*scale); cv2.line(c,(X,0),(X,c.shape[0]),(0,255,255) if gx%(g*2)==0 else (0,128,128),1)
        if gx%(g*2)==0: cv2.putText(c,str(gx),(X+2,12),0,0.4,(0,255,255),1)
    for gy in range((y0//g+1)*g, y1, g):
        Y=int((gy-y0)*scale); cv2.line(c,(0,Y),(c.shape[1],Y),(0,255,255) if gy%(g*2)==0 else (0,128,128),1)
        if gy%(g*2)==0: cv2.putText(c,str(gy),(2,Y-2),0,0.4,(0,255,255),1)
    cv2.putText(c,'f%d'%f,(5,c.shape[0]-8),0,0.6,(0,0,255),2)
    tiles.append(c)
cv2.imwrite(out,np.hstack(tiles) if len(tiles)<4 else np.vstack([np.hstack(tiles[i:i+2]) for i in range(0,len(tiles),2)]))
