import cv2, numpy as np, sys
d='/home/user/quantiphy-challenge/research/next/labaudit/0020/'
pref=sys.argv[1]; idx=[int(x) for x in sys.argv[2].split(',')]; out=sys.argv[3]
ims=[]
for i in idx:
    im=cv2.imread(d+f'frames/{pref}_f{i:02d}.png'); im=cv2.resize(im,(640,360))
    cv2.putText(im,f'{pref} f{i}',(10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2); ims.append(im)
while len(ims)%3: ims.append(np.zeros_like(ims[0]))
rows=[np.hstack(ims[k:k+3]) for k in range(0,len(ims),3)]
cv2.imwrite(d+out,np.vstack(rows))
