import cv2, numpy as np, json, sys
d='/home/user/quantiphy-challenge/research/next/labaudit/0030/frames'
r=sys.argv[1]; idx=[int(x) for x in sys.argv[2].split(',')]; out=sys.argv[3]
x0,y0,x1,y1=[int(v) for v in sys.argv[4].split(',')]
sc=float(sys.argv[5]) if len(sys.argv)>5 else 2
ims=[]
for i in idx:
    im=cv2.imread(f'{d}/{r}_{i:02d}.png')[y0:y1,x0:x1]
    im=cv2.resize(im,None,fx=sc,fy=sc,interpolation=cv2.INTER_NEAREST)
    # grid every 20 px
    for gx in range(0,x1-x0,20): cv2.line(im,(int(gx*sc),0),(int(gx*sc),5),(0,255,0),1)
    for gy in range(0,y1-y0,20): cv2.line(im,(0,int(gy*sc)),(5,int(gy*sc)),(0,255,0),1)
    cv2.putText(im,f'{r}{i}',(5,20),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,255,255),2)
    ims.append(im)
nc=int(sys.argv[6]) if len(sys.argv)>6 else 4
while len(ims)%nc: ims.append(np.zeros_like(ims[0]))
cv2.imwrite(out,np.vstack([np.hstack(ims[k:k+nc]) for k in range(0,len(ims),nc)]))
