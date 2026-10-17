import cv2, sys, numpy as np
out='/home/user/quantiphy-challenge/research/next/audit3/sim2_05/'
for v in sys.argv[1:]:
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4')
    fr=[]
    for i in range(72):
        ok,f=c.read()
        if not ok: break
        if i in (0,24,48,71): fr.append(cv2.resize(f,(1080,540),interpolation=cv2.INTER_AREA))
    img=np.vstack([np.hstack(fr[:2]),np.hstack(fr[2:])])
    img=cv2.resize(img,(1600,800),interpolation=cv2.INTER_AREA)
    cv2.imwrite(out+f'thumb_{v}.png',img)
