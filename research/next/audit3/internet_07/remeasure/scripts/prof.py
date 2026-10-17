from load import load
import numpy as np, cv2
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/internet_0069.mp4')
fr={}
i=0
while True:
    ok,f=c.read()
    if not ok: break
    if i in (66,69,100,101,102): fr[i]=f.astype(np.float32)
    i+=1
bg=(fr[100]+fr[101]+fr[102])/3
for i in (66,69):
    d=np.abs(fr[i]-bg).max(2)
    for r in (650,700,750,800,850,900,950,1000,1030):
        p=d[r-3:r+4].mean(0)
        xs=np.where(p>40)[0]
        print(i,r, xs.min() if len(xs) else None, xs.max() if len(xs) else None, ' '.join(f'{int(v)}' for v in p[ (xs.min()-40 if len(xs) else 0):(xs.min()+40 if len(xs) else 0):4]))
