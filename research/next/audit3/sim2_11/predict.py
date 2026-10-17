import cv2,numpy as np
def frames(v,crop=None):
    cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{v}.mp4'); F=[]
    while True:
        ok,f=cap.read()
        if not ok: break
        F.append(f if crop is None else f[crop[0]:crop[1],crop[2]:crop[3]].copy())
    return F
Y0=550
F=np.array(frames('simulation_0231',(Y0,800,0,1100))); bg=np.median(F,axis=0).astype(np.int16)
masks=[]
for i,f in enumerate(F):
    d=np.abs(f.astype(np.int16)-bg).sum(2)
    m=((d>40)&(f.astype(int).sum(2)<150)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m); k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
    sel=np.zeros(m.shape,bool)
    for j in range(1,n):
        xj,yj,wj,hj,aj=st[j]
        if aj>10 and xj<x+w+10 and xj+wj>x-10 and yj<y+h+10 and yj+hj>y-10: sel|=(lab==j)
    masks.append(sel)
sF=0.714/24/8.88; table=743.0
T=frames('simulation_0233_segmented'); tp=[]
for i,f in enumerate(T):
    m=(f.astype(int).sum(2)<300); m[:,1400:]=0
    m=m.astype(np.uint8); n,lab,st,cen=cv2.connectedComponentsWithStats(m); k=1+np.argmax(st[1:,4]); m=lab==k
    ys,xs=np.nonzero(m); tp.append((xs.max(),xs.min()))
tp=np.array(tp,float)
s=np.arange(14,50); vT=np.polyfit(s,tp[s,0],1)[0]; mn=0.714/24/vT
ss=np.arange(22,50)
for D in [3.5,4.5,5.2,6.0,7.0]:
    hn0=0.24; f=(D-hn0)/mn
    ks=[]; Ls=[]
    for i in ss:
        ys,xs=np.nonzero(masks[i]); xs=xs.astype(float); ys=ys.astype(float)+Y0
        h=(table-ys)*sF
        xn=xs.max(); 
        # nose world X from top-view nose image x (nose height from front)
        hn=h[xs>=xn-2].mean()
        Xn=(tp[i,0]-960)*(D-hn)/f
        # find k s.t. predicted leftmost matches observed: predicted x = 960 + (Xn - k*dX)*f/(D-h)
        dX=(xn-xs)*sF
        best=None
        for kk in np.arange(0.8,1.4,0.002):
            xl=(960+(Xn-kk*dX)*f/(D-h*kk)).min()
            if best is None or abs(xl-tp[i,1])<best[0]: best=(abs(xl-tp[i,1]),kk)
        ks.append(best[1])
    ks=np.array(ks)
    print('D=%.1f f=%.0f  scale factor k (top/front) mean %.3f med %.3f -> top-clip tail-nose x-extent %.3f'%(D,f,ks.mean(),np.median(ks),np.median(ks)*0.613))
