import cv2,numpy as np
c=cv2.VideoCapture('data/QuantiPhy/internet_0036.mp4')
k=0
out=[]
while True:
    ok,im=c.read()
    if not ok: break
    sm=cv2.resize(im,None,fx=0.25,fy=0.25,interpolation=cv2.INTER_AREA).astype(int)
    b,g,r=sm[...,0],sm[...,1],sm[...,2]
    skin=((r-b)>25)&(r>90)
    skin=cv2.morphologyEx(skin.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(skin)
    comps=[(st[i,4],cen[i],st[i,:4]) for i in range(1,n) if st[i,4]>30]
    comps.sort(key=lambda t:-t[0])
    s=[]
    for a,ce,bb in comps[:3]:
        ys,xs=np.nonzero(lab==[i for i in range(1,n) if st[i,4]==a][0])
        s.append(f"A{a} c({ce[0]*4:.0f},{ce[1]*4:.0f}) bb x{bb[0]*4}-{(bb[0]+bb[2])*4} y{bb[1]*4}-{(bb[1]+bb[3])*4}")
    print(k,' | '.join(s))
    k+=1
