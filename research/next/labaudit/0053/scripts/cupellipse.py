import cv2, numpy as np
for prefix in ['o','s','x']:
    fr=[cv2.imread(f'frames/{prefix}_{n:02d}.png').astype(np.float32) for n in range(0,48,2)]
    med=np.median(np.stack(fr),0)
    x0,y0=530,385; crop=med[y0:y0+80,x0:x0+70]
    S=8
    up=cv2.resize(crop,None,fx=S,fy=S,interpolation=cv2.INTER_CUBIC)
    g=up.mean(2).astype(np.float32)
    if prefix=='x':
        gg=up.astype(int); g=(~((gg[...,1]>200)&(gg[...,2]<80)&(gg[...,0]<80))).astype(np.float32)*255
        g=cv2.GaussianBlur(g,(0,0),S*0.5)
    else:
        g=cv2.GaussianBlur(g,(0,0),S*0.6)
    gx=cv2.Sobel(g,cv2.CV_32F,1,0,ksize=3); gy=cv2.Sobel(g,cv2.CV_32F,0,1,ksize=3)
    mag=np.hypot(gx,gy)
    # horizontal profiles: for rows in lid band find outer left/right edges as max gradient within windows
    res=[]
    for yy in np.arange(400,420,0.5):
        r=int((yy-y0)*S)
        L=mag[r,int((544-x0)*S):int((560-x0)*S)]; R=mag[r,int((570-x0)*S):int((586-x0)*S)]
        xl=544+np.argmax(L)/S; xr=570+np.argmax(R)/S
        res.append((yy,xl,xr,xr-xl))
    res=np.array(res)
    # take the rows with max width (smoothed)
    w=np.convolve(res[:,3],np.ones(5)/5,mode='same')
    i=np.argmax(w)
    print(prefix,'max smoothed width %.2f px at row %.1f ; raw widths around:'%(w[i],res[i,0]),np.round(res[max(0,i-6):i+7,3],1))
