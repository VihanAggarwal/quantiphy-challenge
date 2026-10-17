import cv2,numpy as np
v=cv2.VideoCapture('data/QuantiPhy/internet_0003.mp4')
prev=None; cum=np.zeros(2); out=[]
for f in range(37):
    ok,im=v.read()
    if not ok: break
    g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32)
    # camera motion from left table region (no hand) rows 400-1400, cols 0-700
    reg=g[300:1400,0:750]
    if prev is not None:
        (dx,dy),r=cv2.phaseCorrelate(prev,reg); cum+=[dx,dy]
    prev=reg
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    m=((hsv[...,2]<45)).astype(np.uint8)
    m[:, :800]=0; m[:, 1900:]=0; m[:250]=0; m[1300:]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    n,l,st,cen=cv2.connectedComponentsWithStats(m)
    if n>1:
        i=1+np.argmax(st[1:,4]); c=cen[i]; a=st[i,4]
    else: c=(np.nan,np.nan); a=0
    out.append((f,c[0],c[1],a,cum[0],cum[1]))
    print(f,'%.1f %.1f area %d cam %.1f %.1f'%(c[0],c[1],a,cum[0],cum[1]))
