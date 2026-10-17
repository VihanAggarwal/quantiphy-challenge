import cv2, numpy as np, sys
c=sys.argv[1]
cap=cv2.VideoCapture(f'data/QuantiPhy/{c}.mp4')
i=0
while True:
    ok,f=cap.read()
    if not ok: break
    if i%4==0:
        m=(f.min(2)<235)
        g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
        dark=(g<40); dark[:760]=0
        ys,xs=np.nonzero(dark)
        x0,x1=xs.min(),xs.max()
        sub=m[990:1080, max(0,x0-60):x1+60]
        yy,xx=np.nonzero(sub)
        # lowest y per column cluster
        print(i,'dark x %d-%d'%(x0,x1),'max nonwhite y below 990:', 990+yy.max() if len(yy) else None, 'rows>1010 count', (yy>20).sum())
    i+=1
