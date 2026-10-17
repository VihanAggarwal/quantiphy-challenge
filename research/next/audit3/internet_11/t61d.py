import cv2,numpy as np
cap=cv2.VideoCapture('data/QuantiPhy/internet_0061.mp4')
fr=[]
while True:
    ok,im=cap.read()
    if not ok: break
    fr.append(cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32))
bg=np.median(np.stack([fr[i] for i in [60,62,66,70,75,80]]),axis=0)  # acorn elsewhere (bottom) in these? check
for i in range(36,46):
    d=np.abs(fr[i]-bg)
    prof=d[470:590].mean(axis=0)  # mean abs diff along x
    pm=cv2.GaussianBlur(prof.reshape(1,-1),(1,9),0).ravel()
    above=np.where(pm>0.5*np.percentile(pm,99.5))[0]
    # find the main contiguous run
    runs=np.split(above,np.where(np.diff(above)>20)[0]+1)
    runs=[r for r in runs if len(r)>40]
    print(i,[(int(r[0]),int(r[-1]),len(r)) for r in runs], 'max %.0f'%pm.max())
