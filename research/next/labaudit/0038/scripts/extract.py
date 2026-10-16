import cv2, numpy as np, os
B='/home/user/quantiphy-challenge/research/next/labaudit/0038'
for suf,tag in [('', 'o'), ('s','s'), ('x','x')]:
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/captured_0038{suf}.mp4')
    fr=[]
    while True:
        ok,f=c.read()
        if not ok: break
        fr.append(f)
    fr=np.array(fr); np.save(f'{B}/frames/{tag}.npy', fr)
    med=np.median(fr,axis=0).astype(np.uint8); cv2.imwrite(f'{B}/median_{tag}.png', med)
    for i in (0,12,22,28,33,34,36,40,48):
        cv2.imwrite(f'{B}/frames/{tag}_{i:02d}.png', fr[i])
    print(tag, fr.shape)
