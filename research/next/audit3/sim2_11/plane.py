import cv2,numpy as np,sys
for v in ['simulation_0231','simulation_0232']:
    cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4'); F=[]
    while True:
        ok,f=cap.read()
        if not ok: break
        F.append(cv2.cvtColor(f[150:520],cv2.COLOR_BGR2GRAY))
    F=np.array(F).astype(np.int16); bg=np.median(F,axis=0)
    tr=[]
    for i,f in enumerate(F):
        d=(f-bg)
        m=(d>18).astype(np.uint8)   # plane is bright
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        if n<2: tr.append((i,np.nan,np.nan,np.nan,np.nan)); continue
        k=1+np.argmax(st[1:,4])
        if st[k,4]<30: tr.append((i,np.nan,np.nan,np.nan,np.nan)); continue
        ys,xs=np.nonzero(lab==k)
        tr.append((i,xs.min(),xs.max(),cen[k][0],cen[k][1]+150))
    tr=np.array(tr)
    print(v)
    for r in tr:
        if not np.isnan(r[1]): print(' %d L %.0f R %.0f cx %.1f cy %.1f'%tuple(r))
    np.save(f'plane_{v}.npy',tr)
