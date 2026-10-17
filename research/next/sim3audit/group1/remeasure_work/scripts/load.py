import cv2, numpy as np
def frames(path, gray=False, every=1, crop=None):
    c=cv2.VideoCapture(path); out=[]; i=0
    while True:
        ok,f=c.read()
        if not ok: break
        if i%every==0:
            if crop is not None:
                y0,y1,x0,x1=crop; f=f[y0:y1,x0:x1]
            if gray: f=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
            out.append(f)
        i+=1
    return np.array(out)
