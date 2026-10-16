import cv2, numpy as np, sys
# usage: crop.py pre idxlist x0 y0 x1 y1 scale out
pre=sys.argv[1]; idx=[int(x) for x in sys.argv[2].split(',')]
x0,y0,x1,y1=map(int,sys.argv[3:7]); sc=float(sys.argv[7]); out=sys.argv[8]
cols=int(sys.argv[9]) if len(sys.argv)>9 else 3
ims=[]
for i in idx:
    im=cv2.imread(f'frames/{pre}{i:02d}.png')[y0:y1,x0:x1]
    im=cv2.resize(im,None,fx=sc,fy=sc,interpolation=cv2.INTER_CUBIC if sc>1 else cv2.INTER_AREA)
    cv2.putText(im,f'{pre}{i}',(5,25),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2); ims.append(im)
while len(ims)%cols: ims.append(np.zeros_like(ims[0]))
rows=[np.hstack(ims[r*cols:(r+1)*cols]) for r in range(len(ims)//cols)]
cv2.imwrite(out,np.vstack(rows))
