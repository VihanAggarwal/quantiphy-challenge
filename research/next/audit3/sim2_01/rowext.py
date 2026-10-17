import cv2, numpy as np, sys
# rowext.py clip frame x0 x1 y0 y1 step [thr]
c=sys.argv[1]; fr=int(sys.argv[2]); x0,x1,y0,y1,st=map(int,sys.argv[3:8]); thr=int(sys.argv[8]) if len(sys.argv)>8 else 235
cap=cv2.VideoCapture(f'data/QuantiPhy/{c}.mp4'); cap.set(cv2.CAP_PROP_POS_FRAMES,fr); ok,f=cap.read()
m=(f.min(2)<thr)
for y in range(y0,y1,st):
    xs=np.nonzero(m[y,x0:x1])[0]
    if len(xs): print(y, x0+xs[0], x0+xs[-1], xs[-1]-xs[0]+1, 'n',len(xs))
    else: print(y,'-')
