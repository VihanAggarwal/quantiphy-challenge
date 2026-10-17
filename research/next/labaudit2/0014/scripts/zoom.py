import cv2, numpy as np, sys
sys.path.insert(0,'scripts')
from frames import load
r=sys.argv[1]; ks=[int(v) for v in sys.argv[2].split(',')]
cx,cy,h=[int(v) for v in sys.argv[3].split(',')]
sc=int(sys.argv[4]); outp=sys.argv[5]
fr=load(r); tiles=[]
for k in ks:
    c=fr[k][cy-h:cy+h,cx-h:cx+h].copy()
    c=cv2.resize(c,None,fx=sc,fy=sc,interpolation=cv2.INTER_CUBIC)
    # grid every 10 px
    for g in range(0,2*h,10):
        cv2.line(c,(g*sc,0),(g*sc,2*h*sc),(0,255,0) if (cx-h+g)%50 else (0,0,255),1)
        cv2.line(c,(0,g*sc),(2*h*sc,g*sc),(0,255,0) if (cy-h+g)%50 else (0,0,255),1)
    cv2.putText(c,f'{r}{k} x0={cx-h} y0={cy-h}',(3,15),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),1)
    tiles.append(c)
cv2.imwrite(outp,np.hstack(tiles))
