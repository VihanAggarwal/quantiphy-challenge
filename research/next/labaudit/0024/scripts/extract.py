import cv2, numpy as np, os
base='/home/user/quantiphy-challenge/data/QuantiPhy/captured_0024%s.mp4'
out='/home/user/quantiphy-challenge/research/next/labaudit/0024/frames'
for s,tag in [('','o'),('s','s'),('x','x')]:
    c=cv2.VideoCapture(base%s); i=0; fr=[]
    while True:
        ok,f=c.read()
        if not ok: break
        cv2.imwrite(f'{out}/{tag}{i:02d}.png',f); fr.append(f); i+=1
    print(tag,i)
    # montage every 4th frame
    sel=fr[::4]
    th=[cv2.resize(f,(320,180)) for f in sel]
    for k,t in zip(range(0,len(fr),4),th): cv2.putText(t,f'{k} t={k/24:.2f}',(5,20),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,255,255),2)
    while len(th)%4: th.append(np.zeros_like(th[0]))
    rows=[np.hstack(th[i:i+4]) for i in range(0,len(th),4)]
    cv2.imwrite(f'/home/user/quantiphy-challenge/research/next/labaudit/0024/montage_{tag}.png',np.vstack(rows))
