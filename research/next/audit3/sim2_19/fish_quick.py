import cv2, numpy as np
from common import frames
from tmpl import track
for v,thr,ycut in [('simulation_0288',12,None),('simulation_0289',12,1100),('simulation_0291',10,None)]:
    fr=frames(v); n=len(fr)
    bg=np.median(np.stack([fr[i] for i in range(0,n,2)]),axis=0).astype(np.int16)
    rows=[]
    for i in range(2,70):
        im=fr[i].astype(np.int16)
        d=np.abs(im-bg).max(axis=2)
        m=(d>thr).astype(np.uint8)
        if v=='simulation_0288':
            hsv=cv2.cvtColor(fr[i],cv2.COLOR_BGR2HSV)
            sh=(hsv[...,2]<150)&(hsv[...,1]<40)&((bg.mean(axis=2)-im.mean(axis=2))>0)
            m[sh]=0
        if ycut: m[ycut:]=0
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
        nl,lab,st,cen=cv2.connectedComponentsWithStats(m)
        if nl<2: continue
        k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
        rows.append((i,x,y,w,h,a,cen[k][0],cen[k][1]))
    R=np.array(rows,float)
    sl=np.polyfit(R[:,0],R[:,6],1)[0]; sl_l=np.polyfit(R[:,0],R[:,1],1)[0]
    inside=(R[:,1]>5)&(R[:,1]+R[:,3]<2555)
    print(v,'centroid px/frame',round(sl,2),'left-edge px/frame',round(sl_l,2))
    print('  w median',np.median(R[inside,3]),'w p90',np.percentile(R[inside,3],90),'h median',np.median(R[inside,4]),'h p90',np.percentile(R[inside,4],90))
    for r in rows[::8]: print('   ',[round(float(z),1) for z in r])
