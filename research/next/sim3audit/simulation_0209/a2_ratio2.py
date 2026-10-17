import cv2, numpy as np, sys
def load(vid):
    cap=cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/{vid}.mp4'); ok,fr=cap.read(); return fr
def crossing(prof, thr):
    # all crossings of thr; return subpixel positions
    s=np.sign(prof-thr); idx=np.where(s[:-1]*s[1:]<=0)[0]; out=[]
    for i in idx:
        a,b=prof[i],prof[i+1]
        if a!=b: out.append(i+(thr-a)/(b-a))
    return np.array(out)
for vid in sys.argv[1:]:
    im=load(vid).astype(np.float32); Yl=cv2.cvtColor(im.astype(np.uint8),cv2.COLOR_BGR2GRAY).astype(np.float32)
    Yb=cv2.GaussianBlur(Yl,(3,3),0)
    # initial lines (first b-r fit): left x=-1.936y+2104.7, right x=1.8135y+79.6
    ys=np.arange(962,1076); L=[];Rr=[]
    for y in ys:
        xl0=-1.936*y+2104.7; xr0=1.8135*y+79.6
        a=int(xl0)-12; seg=Yb[y,a:a+25]; thr=(seg[:4].mean()+seg[-4:].mean())/2; c=crossing(seg,thr)
        L.append(a+c[np.argmin(np.abs(a+c-xl0))] if len(c) else np.nan)
        a=int(xr0)-12; seg=Yb[y,a:a+25]; thr=(seg[:4].mean()+seg[-4:].mean())/2; c=crossing(seg,thr)
        Rr.append(a+c[np.argmin(np.abs(a+c-xr0))] if len(c) else np.nan)
    L=np.array(L);Rr=np.array(Rr)
    def rfit(y,x):
        m=np.isfinite(x)
        for it in range(4):
            p=np.polyfit(y[m],x[m],1); r=x-np.polyval(p,y); s=np.std(r[m]); m=np.isfinite(x)&(np.abs(r)<max(0.8,2.5*s))
        return p,np.std(r[m]),m.sum()
    pl,sl,nl=rfit(ys,L); pr,sr,nr=rfit(ys,Rr)
    yv=(pr[1]-pl[1])/(pl[0]-pr[0]); xv=np.polyval(pl,yv)
    W=lambda y: np.polyval(pr,y)-np.polyval(pl,y)
    print(vid,'left x=%.4fy+%.1f rms %.2f n=%d | right x=%.4fy+%.1f rms %.2f n=%d | VP (%.1f,%.1f) W(1000)=%.1f'%(pl[0],pl[1],sl,nl,pr[0],pr[1],sr,nr,xv,yv,W(1000)))
    rat=[]
    for y in range(984,1001):
        prof=Yb[y,1170:1410]
        table=np.median(np.r_[Yb[y,1140:1170],Yb[y,1410:1440]]); paper=np.percentile(prof,85)
        thr=(paper+table)/2; c=crossing(prof,thr)
        if len(c)<2: continue
        a,b=1170+c[0],1170+c[-1]
        rat.append((y,a,b,(b-a)/W(y)))
        print('   row %d: table %.0f paper %.0f  letter %.1f..%.1f = %.1f px  W=%.1f ratio %.4f'%(y,table,paper,a,b,b-a,W(y),(b-a)/W(y)))
    np.save(f'/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/{vid}_ratio.npy',np.array(rat))
