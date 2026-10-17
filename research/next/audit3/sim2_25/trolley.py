import cv2,numpy as np
c=cv2.VideoCapture('data/QuantiPhy/simulation_0179.mp4'); fr=[]
while True:
    ok,im=c.read()
    if not ok: break
    fr.append(im[560:920].astype(np.int16))
S=np.stack(fr); bg=np.median(S,0)
L=[]
for f in range(len(fr)):
    d=np.abs(S[f]-bg).max(2)
    m=(d>35).astype(np.uint8); m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if n<2: continue
    i=1+np.argmax(st[1:,4]); x,y,w,h,a=st[i]
    L.append((f,x,x+w-1,y+560,y+h-1+560,a))
L=np.array(L)
for r in L[::6]: print(r)
t=L[:,0]/24.
for k,name in [(1,'left'),(2,'right')]:
    for lo,hi in [(0,59),(5,50),(10,59)]:
        s=(L[:,0]>=lo)&(L[:,0]<=hi)&(L[:,1]>0)&(L[:,2]<1919)
        p=np.polyfit(t[s],L[s,k],2); print(name,lo,hi,'a=%.1f px/s2 v0 %.1f vertex %.3f rms %.2f'%(2*p[0],p[1],-p[1]/(2*p[0]),np.std(L[s,k]-np.polyval(p,t[s]))))
