import cv2, numpy as np, sys
pre=sys.argv[1]; idx=[int(x) for x in sys.argv[2].split(',')]; out=sys.argv[3]
sc=float(sys.argv[4]) if len(sys.argv)>4 else 0.4
ims=[]
for i in idx:
    im=cv2.imread(f'frames/{pre}{i:02d}.png'); im=cv2.resize(im,None,fx=sc,fy=sc)
    cv2.putText(im,str(i),(10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2); ims.append(im)
cols=4
while len(ims)%cols: ims.append(np.zeros_like(ims[0]))
rows=[np.hstack(ims[r*cols:(r+1)*cols]) for r in range(len(ims)//cols)]
cv2.imwrite(out,np.vstack(rows))
