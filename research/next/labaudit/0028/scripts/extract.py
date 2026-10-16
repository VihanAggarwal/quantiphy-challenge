import cv2, numpy as np, os, sys
base='/home/user/quantiphy-challenge/data/QuantiPhy/'
out='/home/user/quantiphy-challenge/research/next/labaudit/0028/frames'
for v in ['captured_0028','captured_0028s','captured_0028x']:
    c=cv2.VideoCapture(base+v+'.mp4'); i=0
    while True:
        ok,f=c.read()
        if not ok: break
        cv2.imwrite(f'{out}/{v}_{i:02d}.png',f); i+=1
    print(v,i)
# montage of the base clip
fr=[cv2.imread(f'{out}/captured_0028_{i:02d}.png') for i in range(49)]
small=[cv2.resize(f,(320,180)) for f in fr]
for i,s in enumerate(small): cv2.putText(s,str(i),(5,20),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2)
while len(small)%7: small.append(np.zeros_like(small[0]))
rows=[np.hstack(small[k:k+7]) for k in range(0,len(small),7)]
cv2.imwrite('/home/user/quantiphy-challenge/research/next/labaudit/0028/montage.png',np.vstack(rows))
