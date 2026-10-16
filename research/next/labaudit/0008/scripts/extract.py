import cv2, sys, numpy as np
base='/home/user/quantiphy-challenge/data/QuantiPhy/'
out='/home/user/quantiphy-challenge/research/next/labaudit/0008/frames/'
for v in ['captured_0008','captured_0008s','captured_0008x']:
    c=cv2.VideoCapture(base+v+'.mp4'); i=0
    while True:
        ok,f=c.read()
        if not ok: break
        cv2.imwrite(f'{out}{v}_f{i:02d}.png',f); i+=1
    print(v,i)
# montage for main
ims=[cv2.imread(f'{out}captured_0008_f{i:02d}.png') for i in range(0,49,4)]
ims=[cv2.resize(x,(320,180)) for x in ims]
while len(ims)%4: ims.append(np.zeros_like(ims[0]))
rows=[np.hstack(ims[i:i+4]) for i in range(0,len(ims),4)]
m=np.vstack(rows)
for k,i in enumerate(range(0,49,4)):
    cv2.putText(m,str(i),((k%4)*320+5,(k//4)*180+20),0,0.7,(0,0,255),2)
cv2.imwrite('/home/user/quantiphy-challenge/research/next/labaudit/0008/montage.png',m)
