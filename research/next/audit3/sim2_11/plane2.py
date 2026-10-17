import cv2,numpy as np
v='simulation_0232'
cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4'); F=[]
while True:
    ok,f=cap.read()
    if not ok: break
    F.append(f[150:560].astype(np.int16))
F=np.array(F); bg=np.median(F,axis=0)
tr=[]
for i,f in enumerate(F):
    d=np.abs(f-bg).sum(2); m=(d>20).astype(np.uint8)
    m[:, :0]=0
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    cand=[(st[j,4],j) for j in range(1,n) if st[j,4]>40 and st[j,1]<380]
    if not cand: continue
    a,k=max(cand); ys,xs=np.nonzero(lab==k)
    tr.append((i,xs.min(),xs.max(),cen[k][0],cen[k][1]+150,a))
for r in tr: print('%d L %d R %d cx %.1f cy %.1f a %d'%r)
