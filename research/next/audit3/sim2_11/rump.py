import cv2,numpy as np
def frames(v,crop=None):
    cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4'); F=[]
    while True:
        ok,f=cap.read()
        if not ok: break
        F.append(f if crop is None else f[crop[0]:crop[1],crop[2]:crop[3]].copy())
    return F
Y0=550
res={}
for v in ['simulation_0231','simulation_0232']:
    F=np.array(frames(v,(Y0,800,0,1100))); bg=np.median(F,axis=0).astype(np.int16); out=[]
    for i,f in enumerate(F):
        d=np.abs(f.astype(np.int16)-bg).sum(2)
        m=((d>40)&(f.astype(int).sum(2)<150)).astype(np.uint8)
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m); k=1+np.argmax(st[1:,4]); m=(lab==k)
        ys,xs=np.nonzero(m)
        rw=m.sum(1)  # row widths
        # torso band: rows where row width >= 55% of max row width
        band=np.nonzero(rw>=0.55*rw.max())[0]
        xsb=[np.nonzero(m[r])[0].min() for r in band]
        out.append((i,xs.max(),min(xsb),np.median(xsb)))
    res[v]=np.array(out,float)
T=frames('simulation_0233_segmented'); out=[]
for i,f in enumerate(T):
    m=(f.astype(int).sum(2)<300); m[:,1400:]=0
    m=m.astype(np.uint8); n,lab,st,cen=cv2.connectedComponentsWithStats(m); k=1+np.argmax(st[1:,4]); m=lab==k
    ys,xs=np.nonzero(m); th=m.sum(0)
    for frac in (0.5,):
        cols=np.nonzero(th>=frac*th.max())[0]
    out.append((i,xs.max(),cols.min(),0))
res['top']=np.array(out,float)
s=np.arange(14,50)
for nm,A in res.items():
    v=np.polyfit(A[s,0],A[s,1],1)[0]
    L=(A[s,1]-A[s,2])/v
    print(nm,'nose v %.3f; nose-to-rump (torso-band leftmost) frames-of-travel mean %.2f med %.2f min %.2f max %.2f ; meters %.3f'%(v,L.mean(),np.median(L),L.min(),L.max(),np.median(L)*0.714/24))
    print('   per-frame', ' '.join('%.1f'%x for x in L))
