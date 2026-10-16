import cv2, numpy as np, sys
D='/home/user/quantiphy-challenge/research/next/labaudit/0047/'
for s in ['','s','x']:
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/captured_0047{s}.mp4')
    i=0
    fr=[]
    while True:
        ok,f=c.read()
        if not ok: break
        cv2.imwrite(D+f'frames/{s or "o"}_{i:02d}.png',f); fr.append(f); i+=1
    # contact sheet every 4 frames, scaled 0.25
    sel=fr[::4]
    th=[cv2.resize(f,(320,180)) for f in sel]
    for k,t in zip(range(0,len(fr),4),th): cv2.putText(t,str(k),(5,20),0,0.6,(0,0,255),2)
    while len(th)%4: th.append(np.zeros_like(th[0]))
    rows=[np.hstack(th[j:j+4]) for j in range(0,len(th),4)]
    cv2.imwrite(D+f'sheet_{s or "o"}.png',np.vstack(rows))
    print(s,i)
