import cv2, numpy as np
V='/home/user/quantiphy-challenge/data/QuantiPhy/internet_0002.mp4'
c=cv2.VideoCapture(V); fr=[]
while True:
    ok,im=c.read()
    if not ok: break
    fr.append(im[900:1500])   # rows 900-1500
F=np.stack(fr); bg=np.median(F,axis=0).astype(np.uint8)
for i in range(4,30,3):
    d=cv2.absdiff(F[i],bg).max(axis=2).astype(float)
    m=(d>40).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    n,l,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
    # length along rows in lower half of car (avoid shadow above)
    rows=range(y+h//2, y+h-15)
    ext=[]
    for r in rows:
        xs=np.where(l[r]==k)[0]
        if len(xs): ext.append(xs.max()-xs.min()+1)
    # width along columns in the middle of car
    cols=range(x+w//3, x+2*w//3)
    wid=[]
    for cc in cols:
        ys=np.where(l[:,cc]==k)[0]
        if len(ys): wid.append(ys.max()-ys.min()+1)
    print(i,'bbox',x,y+900,w,h,'len p90 rows %.0f'%np.percentile(ext,90),'width median %.0f'%np.median(wid), 'width p90 %.0f'%np.percentile(wid,90))
