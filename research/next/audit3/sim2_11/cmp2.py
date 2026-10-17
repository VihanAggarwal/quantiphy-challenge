import cv2,numpy as np
def frames(v,crop=None):
    cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4'); F=[]
    while True:
        ok,f=cap.read()
        if not ok: break
        F.append(f if crop is None else f[crop[0]:crop[1],crop[2]:crop[3]].copy())
    return F
def front_track(v):
    F=np.array(frames(v,(550,800,0,1100))); bg=np.median(F,axis=0).astype(np.int16)
    out=[]
    for i,f in enumerate(F):
        d=np.abs(f.astype(np.int16)-bg).sum(2)
        m=((d>40)&(f.astype(int).sum(2)<150)).astype(np.uint8)
        m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
        n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
        sel=np.zeros(m.shape,bool)
        for j in range(1,n):
            xj,yj,wj,hj,aj=st[j]
            if aj>10 and xj<x+w+10 and xj+wj>x-10 and yj<y+h+10 and yj+hj>y-10: sel|=(lab==j)
        ys,xs=np.nonzero(sel)
        # torso: columns whose vertical thickness >= 60% of max
        th=sel.sum(0); body=np.nonzero(th>=0.6*th.max())[0]
        out.append((i,xs.min(),xs.max(),body.min(),body.max(),xs.mean(),th.max()))
    return np.array(out,float)
def top_track():
    F=frames('simulation_0233_segmented'); out=[]
    for i,f in enumerate(F):
        m=(f.astype(int).sum(2)<300); m[:,1400:]=0
        m=m.astype(np.uint8); n,lab,st,cen=cv2.connectedComponentsWithStats(m)
        k=1+np.argmax(st[1:,4]); m=lab==k
        ys,xs=np.nonzero(m); th=m.sum(0); body=np.nonzero(th>=0.6*th.max())[0]
        out.append((i,xs.min(),xs.max(),body.min(),body.max(),xs.mean(),th.max()))
    return np.array(out,float)
s=np.arange(14,50)
R={'f0231':front_track('simulation_0231'),'f0232':front_track('simulation_0232'),'top':top_track()}
V={}
for nm,A in R.items():
    sl={lab:np.polyfit(A[s,0],A[s,c],1)[0] for c,lab in [(2,'nose'),(4,'bodyR'),(3,'bodyL'),(5,'cx'),(1,'tail')]}
    V[nm]=sl['bodyL']*0.5+sl['bodyR']*0.5
    print(nm,' '.join('%s %.3f'%kv for kv in sl.items()),' maxthick %.0f'%np.median(A[s,6]))
for nm,A in R.items():
    v=V[nm]; tn=(A[s,2]-A[s,1]); bd=(A[s,4]-A[s,3])
    print(nm,'v=%.3f px/f  tail-nose px med %.1f mean %.1f -> %.2f fr ; torso px med %.1f -> %.2f fr; scale %.6f m/px; tail-nose m %.3f torso m %.3f'%(v,np.median(tn),tn.mean(),tn.mean()/v,np.median(bd),np.median(bd)/v,0.714/24/v,tn.mean()*0.714/24/v,np.median(bd)*0.714/24/v))
np.savez('tracks.npz',**R)
