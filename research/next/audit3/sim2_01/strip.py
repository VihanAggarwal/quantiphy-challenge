import cv2, numpy as np, sys
# strip.py clip frames(comma) x0 y0 x1 y1 scale name
c=sys.argv[1]; frs=[int(v) for v in sys.argv[2].split(',')]; x0,y0,x1,y1=map(int,sys.argv[3:7]); sc=float(sys.argv[7]); name=sys.argv[8]
cap=cv2.VideoCapture(f'data/QuantiPhy/{c}.mp4')
out=[]; i=0
while True:
    ok,f=cap.read()
    if not ok: break
    if i in frs:
        cr=f[y0:y1,x0:x1].copy()
        for yy in range((y0//50+1)*50,y1,50):
            cv2.line(cr,(0,yy-y0),(12 if yy%100 else 25,yy-y0),(0,0,255),2)
            if yy%100==0: cv2.putText(cr,str(yy),(28,yy-y0+5),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2)
        for xx in range((x0//50+1)*50,x1,50):
            cv2.line(cr,(xx-x0,0),(xx-x0,12 if xx%100 else 25),(0,0,255),2)
            if xx%100==0: cv2.putText(cr,str(xx),(xx-x0+3,40),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2)
        cv2.putText(cr,'f%d'%i,(x1-x0-70,30),cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,0,0),2)
        out.append(cv2.resize(cr,None,fx=sc,fy=sc))
    i+=1
cv2.imwrite(f'/home/user/quantiphy-challenge/research/next/audit3/sim2_01/png/{name}.png',np.vstack(out))
