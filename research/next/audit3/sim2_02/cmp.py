import cv2, numpy as np
def fr(v,i):
    c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{v}.mp4'); c.set(1,i); return c.read()[1].astype(np.int16)
for i in [0,24,48]:
    a=fr('0236',i); b=fr('0238',i); c=fr('0240',i)
    d1=np.abs(a-b).max(2); d2=np.abs(b-c).max(2)
    for nm,d in [('36v38',d1),('38v40',d2)]:
        m=d>30; ys,xs=np.nonzero(m)
        print(i,nm,'median diff',np.median(d),'n>30',m.sum(), (xs.min(),xs.max(),ys.min(),ys.max()) if m.sum() else None)
