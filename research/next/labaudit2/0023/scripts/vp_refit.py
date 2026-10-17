import numpy as np
D='/home/user/quantiphy-challenge/research/next/labaudit2/0023/'
for V in ['captured_0023x','captured_0023','captured_0023s']:
  for ph in ['slope','table']:
    A=np.load(D+f'frames/avg_{V}_{ph}.npy'); lum=A.mean(-1)
    L=[];R=[]
    for y in range(366,436):
        p=lum[y-300]
        inner=np.median(p[560-400:640-400]) if ph=='table' or y>392 else 245
        def cr(x0,x1,step):
            prev=None
            for x in range(x0,x1,step):
                v=p[x-400]
                if v>230 and prev is not None:
                    # threshold half-way between outside level and white
                    pass
                prev=v
            return None
        # outside level: take value 12 px outside approximate edge
        # approximate edge by first pixel > 200 scanning inward
        xl=None
        for x in range(470,580):
            if p[x-400]>200: xl=x; break
        xr=None
        for x in range(720,600,-1):
            if p[x-400]>200: xr=x; break
        def subpix(xe,dirn):
            out=p[xe-400-6*dirn]; inn=p[xe-400+4*dirn]; mid=0.5*(out+inn)
            xs=np.arange(xe-6*dirn,xe+5*dirn,dirn)
            vals=p[xs-400]
            for i in range(len(xs)-1):
                if (vals[i]-mid)*(vals[i+1]-mid)<=0 and vals[i]!=vals[i+1]:
                    return xs[i]+dirn*(mid-vals[i])/(vals[i+1]-vals[i])
            return np.nan
        L.append((y,subpix(xl,1))); R.append((y,subpix(xr,-1)))
    L=np.array(L); R=np.array(R)
    aL,bL=np.polyfit(L[:,0],L[:,1],1); aR,bR=np.polyfit(R[:,0],R[:,1],1)
    sL=np.std(L[:,1]-(aL*L[:,0]+bL)); sR=np.std(R[:,1]-(aR*R[:,0]+bR))
    yv=(bR-bL)/(aL-aR); xv=aL*yv+bL
    # bootstrap
    rng=np.random.default_rng(0); vs=[]
    for k in range(300):
        i=rng.integers(0,len(L),len(L)); j=rng.integers(0,len(R),len(R))
        a1,b1=np.polyfit(L[i,0],L[i,1],1); a2,b2=np.polyfit(R[j,0],R[j,1],1); vs.append((b2-b1)/(a1-a2))
    print(V,ph,'VP (%.1f, %.1f) boot sd %.1f  resid sd L %.2f R %.2f'%(xv,yv,np.std(vs),sL,sR))
print('--- banded fits & row-wise differences (raw video) ---')
def edges(V,ph,y0,y1):
    A=np.load(D+f'frames/avg_{V}_{ph}.npy'); lum=A.mean(-1); out=[]
    for y in range(y0,y1):
        p=lum[y-300]
        xl=next(x for x in range(470,580) if p[x-400]>200); xr=next(x for x in range(720,600,-1) if p[x-400]>200)
        def subpix(xe,dirn):
            out_=p[xe-400-6*dirn]; inn=p[xe-400+4*dirn]; mid=0.5*(out_+inn)
            xs=np.arange(xe-6*dirn,xe+5*dirn,dirn); vals=p[xs-400]
            for i in range(len(xs)-1):
                if (vals[i]-mid)*(vals[i+1]-mid)<=0 and vals[i]!=vals[i+1]:
                    return xs[i]+dirn*(mid-vals[i])/(vals[i+1]-vals[i])
            return np.nan
        out.append((y,subpix(xl,1),subpix(xr,-1)))
    return np.array(out)
for V in ['captured_0023','captured_0023s','captured_0023x']:
    S=edges(V,'slope',364,436); T=edges(V,'table',364,436)
    for lo,hi in [(364,396),(396,436)]:
        for nm,E_ in [('slope',S),('table',T)]:
            m=(E_[:,0]>=lo)&(E_[:,0]<hi)
            aL,bL=np.polyfit(E_[m,0],E_[m,1],1); aR,bR=np.polyfit(E_[m,0],E_[m,2],1)
            print(V,nm,lo,hi,'VP y %.1f'%((bR-bL)/(aL-aR)), 'slopes %.4f %.4f'%(aL,aR))
    d=S-T
    print(V,'width diff (slope-table) by row:',[('%d'%S[i,0],'%.2f'%((S[i,2]-S[i,1])-(T[i,2]-T[i,1]))) for i in range(0,len(S),8)])
