import cv2,numpy as np
c=cv2.VideoCapture('data/QuantiPhy/simulation_0129.mp4'); fr=[]
while True:
    ok,im=c.read()
    if not ok: break
    fr.append(im)
R=[]
for f,im in enumerate(fr):
    b,g,r=[im[:,:,i].astype(float) for i in range(3)]
    m=((r-g)>60)&((r-b)>60)
    m[:, :800]=False; m[:, 1100:]=False
    ys,xs=np.nonzero(m)
    if len(xs)<20: R.append((f,np.nan,np.nan,0,0,0)); continue
    w=(r-g)[ys,xs]
    R.append((f,(xs*w).sum()/w.sum(),(ys*w).sum()/w.sum(),xs.max()-xs.min()+1,ys.max()-ys.min()+1,len(xs)))
R=np.array(R)
for r in R[::3]: print('%d (%.1f,%.1f) w%d h%d n%d'%tuple(r))
ok=~np.isnan(R[:,2])
for lo,hi in [(0,38),(1,38),(5,35),(10,38),(1,30)]:
    s=ok&(R[:,0]>=lo)&(R[:,0]<=hi)
    p=np.polyfit(R[s,0]/24,R[s,2],2); print(lo,hi,'g_px %.1f vertex %.3f rms %.2f'%(2*p[0],-p[1]/(2*p[0]),np.std(R[s,2]-np.polyval(p,R[s,0]/24))))
# segmented forklift bbox
c=cv2.VideoCapture('data/QuantiPhy/simulation_0129_segmented.mp4'); f=0
while True:
    ok,im=c.read()
    if not ok: break
    m=(im.astype(int).min(2)<235)
    m=cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    big=[st[i] for i in range(1,n) if st[i,4]>200]
    if f%4==0 or f>=36: print('seg',f,[tuple(b) for b in big])
    f+=1
