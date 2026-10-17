import cv2,numpy as np
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0046.mp4')
F={};k=0
while True:
    ok,f=c.read()
    if not ok: break
    F[k]=f.astype(np.int16); k+=1
print('n',len(F))
bg=np.median(np.stack([F[k] for k in list(range(0,12))]),axis=0)
for k in range(14,51):
    d=np.abs(F[k]-bg).max(axis=2)
    band=d[330:470]   # body rows (dark body), avoids rope/handle top
    m=band>40
    cols=np.where(m.sum(0)>60)[0]
    if len(cols)==0: print(k,'none'); continue
    # largest contiguous run
    runs=np.split(cols,np.where(np.diff(cols)>3)[0]+1); r=max(runs,key=len)
    print(k,'L %d R %d mid %.1f w %d'%(r[0],r[-1],(r[0]+r[-1])/2,r[-1]-r[0]))
