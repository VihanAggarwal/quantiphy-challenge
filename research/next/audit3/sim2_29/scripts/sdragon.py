from util import *
for v in ['simulation_0283']:
    fr=frames(v)
    n=len(fr)
    bg=fr[n-1].astype(np.float32) if v.endswith('3') else np.median(np.stack([fr[i] for i in range(0,n,3)]),axis=0).astype(np.float32)
    R=[]
    for i in range(0,n):
        d=np.abs(fr[i].astype(np.float32)-bg).max(axis=2)
        m=(d>40).astype(np.uint8)
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
        nl,lab,st,cen=cv2.connectedComponentsWithStats(m)
        if nl<2: continue
        k=1+np.argmax(st[1:,4]); 
        sel=[q for q in range(1,nl) if st[q,4]>200]
        mm=np.isin(lab,sel); yy,xx=np.nonzero(mm)
        if len(xx)==0: continue
        R.append((i,xx.min(),xx.max(),yy.min(),yy.max(),xx.mean(),yy.mean(),len(xx)))
    R=np.array(R,float)
    print(v)
    for r in R[::4]: print(' ',np.round(r,1))
    ok=(R[:,1]>5)&(R[:,2]<fr[0].shape[1]-5)
    print(' xmin slope',np.polyfit(R[ok,0],R[ok,1],1)[0],'centroid slope',np.polyfit(R[ok,0],R[ok,5],1)[0])
