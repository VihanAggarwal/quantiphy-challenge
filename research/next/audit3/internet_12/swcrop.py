import cv2, numpy as np, sys
p,out,y0,y1,sc=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),float(sys.argv[5])
specs=[a.split(':') for a in sys.argv[6:]]  # frame:x0:x1
cap=cv2.VideoCapture(p); tiles=[]
g=50
for f,x0,x1 in specs:
    f,x0,x1=int(f),int(x0),int(x1)
    cap.set(cv2.CAP_PROP_POS_FRAMES,f); ok,im=cap.read()
    c=cv2.resize(im[y0:y1,x0:x1],None,fx=sc,fy=sc,interpolation=cv2.INTER_AREA)
    for gx in range((x0//g+1)*g,x1,g):
        X=int((gx-x0)*sc); cv2.line(c,(X,0),(X,c.shape[0]),(0,255,255) if gx%100==0 else (0,120,120),1)
        if gx%100==0: cv2.putText(c,str(gx),(X+2,12),0,0.35,(0,0,255),1)
    for gy in range((y0//g+1)*g,y1,g):
        Y=int((gy-y0)*sc); cv2.line(c,(0,Y),(c.shape[1],Y),(0,255,255) if gy%100==0 else (0,120,120),1)
        if gy%100==0: cv2.putText(c,str(gy),(2,Y-2),0,0.35,(0,0,255),1)
    cv2.putText(c,'f%d'%f,(5,c.shape[0]-6),0,0.6,(0,0,255),2)
    tiles.append(c)
w=max(t.shape[1] for t in tiles)
tiles=[cv2.copyMakeBorder(t,0,4,0,w-t.shape[1],cv2.BORDER_CONSTANT) for t in tiles]
cv2.imwrite(out,np.vstack(tiles))
