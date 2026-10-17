import cv2, numpy as np, sys
W='research/next/audit3/internet_10/remeasure/'
sh=np.loadtxt(W+'shifts_clean.txt'); dx=(sh[:,0]+sh[:,2])/2; dy=(sh[:,1]+sh[:,3])/2
c=cv2.VideoCapture('data/QuantiPhy/internet_0054.mp4')
spec=eval(sys.argv[1])  # list of (frame,x0,y0,w,h,scale,name)
for fr,x0,y0,w,h,s,name in spec:
    c.set(cv2.CAP_PROP_POS_FRAMES,fr); ok,f=c.read()
    M=np.float32([[1,0,-dx[fr]],[0,1,-dy[fr]]])
    g=cv2.warpAffine(f,M,(3840,2160),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
    cr=g[y0:y0+h,x0:x0+w].copy()
    cr=cv2.resize(cr,None,fx=s,fy=s,interpolation=cv2.INTER_NEAREST)
    step=10
    for yy in range(0,h,step):
        L=12 if (y0+yy)%50==0 else 5
        cv2.line(cr,(0,int(yy*s)),(L,int(yy*s)),(0,0,255),1)
        if (y0+yy)%50==0: cv2.putText(cr,str(y0+yy),(14,int(yy*s)+4),cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,0,255),1)
    for xx in range(0,w,step):
        L=12 if (x0+xx)%50==0 else 5
        cv2.line(cr,(int(xx*s),0),(int(xx*s),L),(0,0,255),1)
        if (x0+xx)%100==0: cv2.putText(cr,str(x0+xx),(int(xx*s)+2,24),cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,0,255),1)
    cv2.imwrite(W+name,cr)
