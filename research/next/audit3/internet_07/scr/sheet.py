import cv2, sys, numpy as np
p, out = sys.argv[1], sys.argv[2]
frames = [int(x) for x in sys.argv[3].split(',')]
sc = float(sys.argv[4]) if len(sys.argv)>4 else 0.25
cap = cv2.VideoCapture(p)
imgs=[]
for f in frames:
    cap.set(cv2.CAP_PROP_POS_FRAMES, f)
    ok, im = cap.read()
    im = cv2.resize(im, None, fx=sc, fy=sc)
    cv2.putText(im, str(f), (5,25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
    imgs.append(im)
n=len(imgs); cols=min(4,n); rows=(n+cols-1)//cols
h,w=imgs[0].shape[:2]
S=np.zeros((rows*h, cols*w,3),np.uint8)
for i,im in enumerate(imgs):
    S[(i//cols)*h:(i//cols+1)*h,(i%cols)*w:(i%cols+1)*w]=im
cv2.imwrite(out,S)
