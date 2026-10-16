import cv2, numpy as np, sys
d='/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure/frames'
v=sys.argv[1]; idx=[int(x) for x in sys.argv[2].split(',')]; scale=float(sys.argv[3]) if len(sys.argv)>3 else 0.4
ims=[]
for i in idx:
    f=cv2.imread(f'{d}/{v}_{i:02d}.png'); f=cv2.resize(f,None,fx=scale,fy=scale)
    cv2.putText(f,f'{v} {i}',(10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2); ims.append(f)
cols=int(sys.argv[4]) if len(sys.argv)>4 else 3
while len(ims)%cols: ims.append(np.zeros_like(ims[0]))
rows=[np.hstack(ims[i:i+cols]) for i in range(0,len(ims),cols)]
cv2.imwrite(f'/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure/sheet_{v}.png',np.vstack(rows))
