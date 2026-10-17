import cv2, numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0223.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32))
fr=np.array(fr)
last=fr[-1]
for i in range(len(fr)):
    dprev=np.abs(fr[i]-fr[i-1]).mean() if i else -1
    d=np.abs(fr[i]-last)
    d[:, :800]=0; d[:, 1120:]=0
    m=(d>40).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: print(i,'dprev %.3f'%dprev,'none'); continue
    k=1+np.argmax(st[1:,4])
    print(i,'dprev %.3f'%dprev, st[k].tolist(), 'cen %.1f %.1f'%tuple(cen[k]))
