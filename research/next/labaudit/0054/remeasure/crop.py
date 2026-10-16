import cv2, numpy as np, sys
d='/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure/frames'
# usage: crop.py v frames x0 y0 x1 y1 scale cols outname
v=sys.argv[1]; idx=[int(x) for x in sys.argv[2].split(',')]
x0,y0,x1,y1=map(int,sys.argv[3:7]); s=float(sys.argv[7]); cols=int(sys.argv[8]); name=sys.argv[9]
ims=[]
for i in idx:
    f=cv2.imread(f'{d}/{v}_{i:02d}.png')[y0:y1,x0:x1]; f=cv2.resize(f,None,fx=s,fy=s,interpolation=cv2.INTER_CUBIC)
    cv2.putText(f,f'{v} {i}',(5,25),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2); ims.append(f)
while len(ims)%cols: ims.append(np.zeros_like(ims[0]))
rows=[np.hstack(ims[i:i+cols]) for i in range(0,len(ims),cols)]
cv2.imwrite(f'/home/user/quantiphy-challenge/research/next/labaudit/0054/remeasure/{name}.png',np.vstack(rows))
