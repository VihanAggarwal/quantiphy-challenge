import cv2, numpy as np
from common import frames
for v in ['simulation_0079','simulation_0080','simulation_0081']:
    fr=frames(v); n=len(fr)
    bg=np.median(np.stack([fr[i] for i in range(0,n,1)]),axis=0).astype(np.int16)
    out={}
    for i in range(n):
        im=fr[i]; hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
        cy=(hsv[...,0]>80)&(hsv[...,0]<100)&(hsv[...,1]>80)&(hsv[...,2]>100)
        cy=cv2.morphologyEx(cy.astype(np.uint8),cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
        ys,xs=np.nonzero(cy)
        bike=None
        if len(xs)>50 and xs.min()>2 and xs.max()<1917:
            bike=(xs.min(),xs.max(),np.median(ys))
        elif len(xs)>50: bike=(xs.min(),xs.max(),np.median(ys),'clipped')
        # walker: dark hair blob in upper half (y<540): very dark pixels, away from bike rows
        g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
        d=np.abs(im.astype(np.int16)-bg).max(axis=2)
        wm=(d>30); wm[560:]=False
        wm=cv2.morphologyEx(wm.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        nl,lab,st,cen=cv2.connectedComponentsWithStats(wm)
        walker=None
        if nl>1:
            k=1+np.argmax(st[1:,4]); walker=(cen[k][0],cen[k][1],st[k][4])
        # head: dark blob within walker bbox
        head=None
        if walker:
            hm=((g<70)&(wm>0)).astype(np.uint8)
            hm=cv2.morphologyEx(hm,cv2.MORPH_OPEN,np.ones((9,9),np.uint8))
            nl2,lab2,st2,cen2=cv2.connectedComponentsWithStats(hm)
            if nl2>1:
                k2=1+np.argmax(st2[1:,4]); head=(cen2[k2][0],cen2[k2][1],st2[k2][4])
        out[i]=(bike,walker,head)
    print(v,n)
    for i in [1,4,8,10,11,12,13,14,16,20,22,23,24,25,26,28]:
        if i in out:
            b,w,h=out[i]
            print(' ',i,'bike',None if b is None else tuple(round(float(z),1) if not isinstance(z,str) else z for z in b),
                  'walker',None if w is None else (round(w[0],1),round(w[1],1),int(w[2])),'head',None if h is None else (round(h[0],1),round(h[1],1),int(h[2])))
    np.save if False else None
    import json
    json.dump({str(k):[None if b is None else [float(z) for z in b[:3]], None if w is None else [float(z) for z in w], None if h is None else [float(z) for z in h]] for k,(b,w,h) in out.items()}, open(f'bike_{v}.json','w'))
