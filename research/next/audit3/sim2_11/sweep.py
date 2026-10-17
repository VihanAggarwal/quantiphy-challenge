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
fr=[]
for i,f in enumerate(F):
    d=np.abs(f.astype(np.int16)-bg).sum(2)
    full=(d>45).astype(np.uint8)
    m=((d>40)&(f.astype(int).sum(2)<150)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m); k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
    sel=np.zeros(m.shape,bool)
    for j in range(1,n):
        xj,yj,wj,hj,aj=st[j]
        if aj>10 and xj<x+w+10 and xj+wj>x-10 and yj<y+h+10 and yj+hj>y-10: sel|=(lab==j)
    ys,xs=np.nonzero(sel)
    xn=xs.max(); yn=ys[xs>=xn-2].mean()
    yt=ys.min(); xt=xs[ys<=yt+2].mean(); xl=xs.min(); yl=ys[xs<=xl+2].mean()
    # full bbox incl white paws, restricted near the dark bbox
    fy,fx=np.nonzero(full[:, max(0,xs.min()-40):xs.max()+40]); fx=fx+max(0,xs.min()-40)
    ok=(fy>=ys.min()-5)
    fr.append((i,xn,yn+Y0,xt,yt+Y0,xl,yl+Y0,fx[ok].min(),fx[ok].max(),fy[ok].max()+Y0))
fr=np.array(fr,float)
s=np.arange(14,50)
vF=np.polyfit(fr[s,0],(fr[s,1]+fr[s,5])/2,1)[0]; sF=0.714/24/vF
table=np.median(fr[:,9])
print('front v %.3f px/f scale %.6f table row %.1f'%(vF,sF,table))
hn=(table-fr[:,2])*sF; ht=(table-fr[:,4])*sF; hl=(table-fr[:,6])*sF
print('nose height mean %.3f, tail-top height mean %.3f, leftmost-pt height mean %.3f'%(hn[s].mean(),ht[s].mean(),hl[s].mean()))
Lfront_dark=(fr[:,1]-fr[:,5])*sF; Lfront_full=(fr[:,8]-fr[:,7])*sF
print('front dark x-extent mean %.3f med %.3f ; full(paws) mean %.3f med %.3f min %.3f max %.3f; frame0 dark %.3f full %.3f'%(Lfront_dark[s].mean(),np.median(Lfront_dark[s]),Lfront_full[s].mean(),np.median(Lfront_full[s]),Lfront_full[s].min(),Lfront_full[s].max(),Lfront_dark[0],Lfront_full[0]))
# top
T=frames('simulation_0233_segmented'); tp=[]
for i,f in enumerate(T):
    m=(f.astype(int).sum(2)<300); m[:,1400:]=0
    m=m.astype(np.uint8); n,lab,st,cen=cv2.connectedComponentsWithStats(m); k=1+np.argmax(st[1:,4]); m=lab==k
    ys,xs=np.nonzero(m); tp.append((i,xs.max(),xs.min()))
tp=np.array(tp,float)
vT=np.polyfit(tp[s,0],tp[s,1],1)[0]; mn=0.714/24/vT
print('top nose v %.3f scale %.6f'%(vT,mn))
ss=np.arange(22,50)  # tail tip visible in top view
for D in [3.5,4.5,5.2,6.0,7.0,10.0,100.0]:
    f=(D-hn[ss].mean())/mn
    L=(tp[ss,1]-960)*(D-hn[ss])/f - (tp[ss,2]-960)*(D-hl[ss])/f
    print('D=%.1f f=%.0f  corrected top x-extent mean %.3f med %.3f  (frames22-49); front dark same frames %.3f'%(D,f,L.mean(),np.median(L),Lfront_dark[ss].mean()))
