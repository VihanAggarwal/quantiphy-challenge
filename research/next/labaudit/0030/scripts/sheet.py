import cv2, numpy as np, sys
r=sys.argv[1]; idx=[int(x) for x in sys.argv[2].split(',')]; out=sys.argv[3]
d='/home/user/quantiphy-challenge/research/next/labaudit/0030/frames'
ims=[]
for i in idx:
    im=cv2.imread(f'{d}/{r}_{i:02d}.png'); im=cv2.resize(im,(640,360))
    cv2.putText(im,f'{r}{i} t={i/24:.3f}',(10,30),cv2.FONT_HERSHEY_SIMPLEX,0.9,(0,255,255),2)
    ims.append(im)
while len(ims)%3: ims.append(np.zeros_like(ims[0]))
rows=[np.hstack(ims[k:k+3]) for k in range(0,len(ims),3)]
cv2.imwrite(out,np.vstack(rows))
