import cv2, numpy as np, sys
vid=sys.argv[1]
c=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4')
F=[]
while True:
    ok,f=c.read()
    if not ok: break
    F.append(f[380:620, 380:700].copy())   # roi y,x
F=np.array(F).astype(np.float32)
med=np.median(F,axis=0)
for i,f in enumerate(F):
    d=np.abs(f-med).sum(axis=2)
    m=(d>60).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: print(i,'none'); continue
    k=1+np.argmax(st[1:,4])
    x,y,w,h,a=st[k]
    print(i, 'cx=%.1f cy=%.1f w=%d h=%d a=%d'%(cen[k][0]+380,cen[k][1]+380,w,h,a), 'eqd=%.1f'%(2*np.sqrt(a/np.pi)))
