import cv2, numpy as np, sys
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/'
D='/home/user/quantiphy-challenge/research/next/labaudit/0022/'
for r in ['','s','x']:
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/captured_0022{r}.mp4')
    fr=[]
    while True:
        ok,im=c.read()
        if not ok: break
        fr.append(im)
    fr=np.array(fr); np.save(S+f'fr0022{r}.npy',fr); print(r,fr.shape)
    # montage every 4th frame, downscaled
    idx=list(range(0,len(fr),4))
    th=[cv2.resize(fr[i],(320,180)) for i in idx]
    for t,i in zip(th,idx): cv2.putText(t,str(i),(5,20),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2)
    while len(th)%4: th.append(np.zeros_like(th[0]))
    rows=[np.hstack(th[k:k+4]) for k in range(0,len(th),4)]
    cv2.imwrite(D+f'montage_{r or "o"}.png',np.vstack(rows))
    for i in [0,14,19,24,29,38,48]:
        cv2.imwrite(D+f'frames/{r or "o"}_{i:02d}.png',fr[i])
