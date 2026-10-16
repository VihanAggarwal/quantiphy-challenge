import cv2, numpy as np, sys
d='/home/user/quantiphy-challenge/research/next/labaudit/0020/'
# usage: crop.py pref frames x0 y0 x1 y1 scale out
pref=sys.argv[1]; idx=[int(x) for x in sys.argv[2].split(',')]
x0,y0,x1,y1=map(int,sys.argv[3:7]); s=float(sys.argv[7]); out=sys.argv[8]
ims=[]
for i in idx:
    im=cv2.imread(d+f'frames/{pref}_f{i:02d}.png')[y0:y1,x0:x1]
    im=cv2.resize(im,None,fx=s,fy=s,interpolation=cv2.INTER_CUBIC)
    cv2.putText(im,f'{pref} f{i}',(5,20),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2); ims.append(im)
ncol=int(sys.argv[9]) if len(sys.argv)>9 else 4
while len(ims)%ncol: ims.append(np.zeros_like(ims[0]))
rows=[np.hstack(ims[k:k+ncol]) for k in range(0,len(ims),ncol)]
cv2.imwrite(d+out,np.vstack(rows))
