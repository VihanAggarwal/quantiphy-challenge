import cv2, numpy as np
c = cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0112_segmented.mp4')
for fi in [20,25,30]:
    c.set(cv2.CAP_PROP_POS_FRAMES, fi); ok,f=c.read()
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(int)
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    # tyre = dark low-saturation pixels
    m=(g<70)&(hsv[...,1]<90)
    sub=m[440:538]
    cols=sub.sum(0)
    runs=np.nonzero(cols>8)[0]
    # split into groups
    groups=np.split(runs, np.nonzero(np.diff(runs)>3)[0]+1)
    for gr in groups:
        if len(gr)<30: continue
        x0,x1=gr[0],gr[-1]
        rows=np.nonzero(m[400:545,x0:x1+1].sum(1)>3)[0]+400
        print(fi,'x',x0,x1,'w',x1-x0+1,'y',rows.min(),rows.max(),'h',rows.max()-rows.min()+1)
