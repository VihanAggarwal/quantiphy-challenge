# usage: ruler_crop.py video out.png scale "f:x0:y0:w:h" ...  -> stacked crops with pixel rulers (full-res coords)
import cv2, numpy as np, sys
P=sys.argv[1]; out=sys.argv[2]; S=int(sys.argv[3]); specs=[list(map(int,s.split(':'))) for s in sys.argv[4:]]
want={s[0]:s for s in specs}
c=cv2.VideoCapture(P); i=0; crops={}
mx=max(s[0] for s in specs)
while i<=mx:
    ok,im=c.read()
    if not ok: break
    if i in want:
        f,x0,y0,w,h=want[i]
        cr=cv2.resize(im[y0:y0+h,x0:x0+w],(w*S,h*S),interpolation=cv2.INTER_CUBIC)
        for yy in range(0,h,5):
            L=6 if yy%10 else (14 if yy%50 else 30)
            cv2.line(cr,(0,yy*S),(L,yy*S),(0,0,255),1)
            if yy%50==0: cv2.putText(cr,str(y0+yy),(32,yy*S+5),0,0.45,(0,0,255),1)
        for xx in range(0,w,5):
            L=6 if xx%10 else (14 if xx%50 else 30)
            cv2.line(cr,(xx*S,0),(xx*S,L),(255,255,0),1)
            if xx%50==0: cv2.putText(cr,str(x0+xx),(xx*S+2,44),0,0.45,(255,255,0),1)
        cv2.putText(cr,'f%d'%f,(w*S-60,20),0,0.6,(0,255,255),2)
        crops[i]=cr
    i+=1
W=max(cr.shape[1] for cr in crops.values())
rows=[cv2.copyMakeBorder(crops[s[0]],0,4,0,W-crops[s[0]].shape[1],cv2.BORDER_CONSTANT) for s in specs]
cv2.imwrite(out,np.vstack(rows))
