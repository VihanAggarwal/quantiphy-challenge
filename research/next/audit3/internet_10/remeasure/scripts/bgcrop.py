import cv2, numpy as np, sys
W='research/next/audit3/internet_10/remeasure/'
bg=cv2.imread('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/i54rm/bg_380_1200.png')
OFF=380
spec=eval(sys.argv[1])
for x0,y0,w,h,s,name in spec:
    cr=bg[y0-OFF:y0-OFF+h,x0:x0+w].copy()
    cr=cv2.resize(cr,None,fx=s,fy=s,interpolation=cv2.INTER_NEAREST if s>=2 else cv2.INTER_AREA)
    for yy in range(0,h,10):
        L=12 if (y0+yy)%50==0 else 5
        cv2.line(cr,(0,int(yy*s)),(L,int(yy*s)),(0,0,255),1)
        if (y0+yy)%50==0: cv2.putText(cr,str(y0+yy),(14,int(yy*s)+4),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,255),1)
    for xx in range(0,w,10):
        L=12 if (x0+xx)%50==0 else 5
        cv2.line(cr,(int(xx*s),0),(int(xx*s),L),(0,0,255),1)
        if (x0+xx)%100==0: cv2.putText(cr,str(x0+xx),(int(xx*s)+2,26),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,0,255),1)
    cv2.imwrite(W+name,cr)
