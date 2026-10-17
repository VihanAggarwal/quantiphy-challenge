import cv2,numpy as np
caps={c:cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{c}.mp4') for c in ['0303','0305','0307']}
fr={c:[] for c in caps}
for c,cap in caps.items():
    while True:
        ok,f=cap.read()
        if not ok: break
        fr[c].append(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)[::4,::4].astype(np.float32))
# 0303 mask: dark
for i in [1,10,25,50,71]:
    m=fr['0303'][i]<110; m[:22]=0; m[-22:]=0
    ys,xs=np.nonzero(m)
    print(i,'0303 bbox',xs.min()*4,xs.max()*4,ys.min()*4,ys.max()*4)
# compare 0303 frame i to 0305 frames j via mask correlation using 0305 diff from median
for c in ['0305','0307']:
    med=np.median(np.stack(fr[c][::3]),axis=0)
    for i in [1,25,50,71]:
        d=np.abs(fr[c][i]-med)>25; d[:22]=0; d[-22:]=0
        ys,xs=np.nonzero(d)
        print(c,i,'diff bbox',np.percentile(xs,1)*4,np.percentile(xs,99)*4,np.percentile(ys,1)*4,np.percentile(ys,99)*4)
