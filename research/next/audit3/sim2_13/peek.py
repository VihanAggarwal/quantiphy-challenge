import cv2, sys, numpy as np
c=sys.argv[1]; frames=[int(x) for x in sys.argv[2].split(',')]
cap=cv2.VideoCapture(f'data/QuantiPhy/simulation_{c}.mp4')
imgs=[]
for f in frames:
    cap.set(cv2.CAP_PROP_POS_FRAMES,f); ok,im=cap.read()
    im=cv2.resize(im,(640,360)); cv2.putText(im,str(f),(10,30),0,1,(0,0,255),2); imgs.append(im)
while len(imgs)%2: imgs.append(np.zeros_like(imgs[0]))
rows=[np.hstack(imgs[i:i+2]) for i in range(0,len(imgs),2)]
cv2.imwrite(f'research/next/audit3/sim2_13/img/peek_{c}.png',np.vstack(rows))
