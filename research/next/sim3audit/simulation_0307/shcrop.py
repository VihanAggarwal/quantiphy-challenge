import cv2,numpy as np
cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0305.mp4')
for i in [20,40,60]:
    cap.set(cv2.CAP_PROP_POS_FRAMES,i); ok,f=cap.read()
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
    m=(g<90); m[:900 if i==20 else 450]=0; m[-85:]=0
    ys,xs=np.nonzero(m)
    print(i,xs.min(),xs.max(),ys.min(),ys.max())
    x0,x1,y0,y1=xs.min()-30,xs.max()+30,ys.min()-30,ys.max()+30
    cr=f[max(y0,0):y1,max(x0,0):x1]
    s=1200/cr.shape[1]
    cv2.imwrite(f'frames/shadow_{i:03d}.png',cv2.resize(cr,None,fx=s,fy=s))
