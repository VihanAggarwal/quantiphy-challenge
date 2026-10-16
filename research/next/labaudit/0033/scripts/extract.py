import cv2, numpy as np, sys
base='/home/user/quantiphy-challenge/data/QuantiPhy/captured_0033%s.mp4'
out='/home/user/quantiphy-challenge/research/next/labaudit/0033/frames/'
for s in ['','s','x']:
    c=cv2.VideoCapture(base%s); fr=[]
    while True:
        ok,f=c.read()
        if not ok: break
        fr.append(f)
    fr=np.array(fr)
    # contact sheet every 4 frames
    idx=list(range(0,len(fr),4))
    th=[cv2.resize(fr[i],(320,180)) for i in idx]
    for t,i in zip(th,idx): cv2.putText(t,str(i),(5,20),0,0.7,(0,0,255),2)
    while len(th)%4: th.append(np.zeros_like(th[0]))
    rows=[np.hstack(th[k:k+4]) for k in range(0,len(th),4)]
    cv2.imwrite(out+'sheet_%s.png'%(s or 'o'),np.vstack(rows))
    print(s,fr.shape)
