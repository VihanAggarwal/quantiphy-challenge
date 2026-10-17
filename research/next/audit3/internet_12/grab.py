import cv2, sys
p, fr, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
scale = float(sys.argv[4]) if len(sys.argv)>4 else 0.5
crop = sys.argv[5] if len(sys.argv)>5 else None
cap=cv2.VideoCapture(p); cap.set(cv2.CAP_PROP_POS_FRAMES, fr); ok,im=cap.read()
if crop:
    x0,y0,x1,y1=map(int,crop.split(','))
    im=im[y0:y1,x0:x1]
im=cv2.resize(im,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA if scale<1 else cv2.INTER_CUBIC)
cv2.imwrite(out,im)
