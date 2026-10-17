import cv2,numpy as np
im=cv2.imread('full48.png'); g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
lsd=cv2.createLineSegmentDetector()
L=lsd.detect(g)[0].reshape(-1,4)
ln=np.hypot(L[:,2]-L[:,0],L[:,3]-L[:,1])
L=L[ln>80]; ln=ln[ln>80]
o=np.argsort(-ln)
vis=im.copy()
for k,i in enumerate(o[:40]):
    x1,y1,x2,y2=L[i]; ang=np.degrees(np.arctan2(y2-y1,x2-x1))
    print(k,np.round(L[i],1),round(ln[i]),round(ang,1))
    cv2.line(vis,(int(x1),int(y1)),(int(x2),int(y2)),(0,0,255),2)
    cv2.putText(vis,str(k),(int((x1+x2)/2),int((y1+y2)/2)),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,0),2)
cv2.imwrite('lines48.png',cv2.resize(vis,None,fx=0.6,fy=0.6))
