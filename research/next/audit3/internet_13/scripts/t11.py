import cv2,numpy as np
v=cv2.VideoCapture('data/QuantiPhy/internet_0011.mp4')
fr=[]
while True:
    ok,im=v.read()
    if not ok: break
    fr.append(cv2.resize(im,None,fx=0.25,fy=0.25,interpolation=cv2.INTER_AREA))
fr=np.array(fr); print(fr.shape)
bg=np.median(fr[::6],axis=0).astype(np.uint8)
for f in range(0,len(fr),6):
    d=np.abs(fr[f].astype(int)-bg.astype(int)).sum(2)
    m=(d>60).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,l,st,cen=cv2.connectedComponentsWithStats(m)
    bl=[(st[i,4],cen[i]*4) for i in range(1,n) if st[i,4]>40]
    # whiteness of blob
    s=[]
    for i in range(1,n):
        if st[i,4]>40:
            pix=fr[f][l==i]; s.append('a%d (%.0f,%.0f) bright%.0f'%(st[i,4],cen[i][0]*4,cen[i][1]*4,pix.mean()))
    print(f,s)
